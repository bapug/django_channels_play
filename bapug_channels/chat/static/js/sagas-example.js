import {
  all, delay,
  take, takeLatest, takeEvery,
  put, fork, call, select, cancelled,
} from 'redux-saga/effects'
import {eventChannel, END} from 'redux-saga'
import axioscore from 'axios'
import {captureEvent,
  captureMessage, captureException} from '@sentry/browser'

import {actions} from '~/redux-page'
import {moduleConfig} from './index'
import * as types from './constants'

const get_axios = () => {
  const {axios_config} = moduleConfig
  return axioscore.create(axios_config)
}

function setupChannelsEvent(socket) {
  
  return eventChannel(emitter => {
    
    socket.onopen = () => {
      // ToDo: refactor this into a callback
      socket.send(JSON.stringify({'action': 'getLastUpdateTime'}))
    }
    
    socket.onerror = (error) => {
      captureMessage(`Websocket error ${error}`)
    }
    
    socket.onclose = function(e) {
      emitter(END)
    }
    
    socket.onmessage = function(e) {
      return emitter(e.data)
    }
    
    return () => {
      socket.close()
    }
    
  })
}

function* watchInternal(channel) {
  try {
    while (true) {
      const packet = yield take(channel)
      try {
        const data = JSON.parse(packet)
        let {action, payload} = data
        
        try {
          payload = JSON.parse(payload)
        } catch(e) {
          // I guess it wasn't JSON after all.
        }
        
        if (action in actions) {
          yield put(actions[action](payload))
        } else {
          captureEvent({
            message: 'Invalid action from websockets',
            extra: {
              action: action,
            }
          })
        }
      } catch (e) {
        captureException(e)
      }
    }
  } finally {
    if (yield cancelled()) {
      channel.close()
    }
  }
}

/**
 * channelsConnectionManager
 *
 * Generator that will create a websocket connection,
 * setup a eventChannel to receive messages, and reconnect
 * if the connection is closed for any reason.
 * @returns {IterableIterator<CallEffect|IterableIterator<*>>}
 */
function* channelsConnectionManager() {
  const {comment_group, enable_wss} = moduleConfig

  if (!enable_wss) {
    return yield delay(1)
  }
  
  const delayMin = 4
  const delayMax = 8
  
  const url = `wss://${window.location.host}/ws/comments/${comment_group}/`
  
  while (true) {
    try {
      const socket = new WebSocket(url)
      let channel = yield call(setupChannelsEvent, socket)
      
      yield watchInternal(channel)
    } catch(e) {
      // If the server is down, this can happen. We will fall out to
      // the retries, and attempt a new connection hopefully.
      captureException(e)
    }
    
    // At this point our channel has disconnected
    const dval = Math.floor(1000 * (delayMin + Math.random() * (delayMax - delayMin)))
    yield delay(dval)
  }
}

function* getComments() {
  const axios = get_axios()
  const {query_url, page_id} = moduleConfig
  
  
  const url = query_url
    .replace(/str:group/, 'group')
    .replace(/int:page_id/, page_id)
  
  const results = yield axios.get(url)
  
  // Results format:
  /**
   data = {
   'comments': [
      {
        id: int,
        comment: string,
        comment_rendered: string,
        user: {},
        likes: int,
        parent_id: int -> null or id for parent of this comment>
      },
      ...
   ]
   }
   */
  yield put(actions.updateTTComments(results.data))
}

/***
 * Add a comment
 *
 * Some notes on content:
 *  page_url looks like this: '/gardens/garden-slug/'
 *  add_url looks like this: '/talk/add/str:group/slug:page/'
 *  So, we replace the group 'placeholder' and the page placeholders with our new values
 * @param payload
 * @returns {IterableIterator<*>}
 */
function* addComment({payload: data}) {
  const {page_url, add_url, page_id} = moduleConfig
  
  // Split the group, which should be gardens, plants, etc
  // And the slug, which should be the garden or plant, etc.
  const [group, slug] = page_url.split('/').slice(1) //?
  
  const url = add_url
    .replace(/str:group/, group)
    .replace(/int:page_id/, page_id)
  
  const axios = get_axios()
  try {
    const result = yield call(axios.post, url, data)
  } catch (e) {
    captureException(e)
  }
}

function* updateComment({payload: data}) {
  const {page_url, update_url, page_id} = moduleConfig
  
  const [group, slug] = page_url.split('/').slice(1) //?
  
  const {id} = data
  
  const url = update_url
    .replace(/str:group/, group)
    .replace(/int:page_id/, page_id)
    .replace(/int:comment_id/, id)
  
  const axios = get_axios()
  try {
    yield put(actions.updatingComment({id: id}))
    const result = yield call(axios.patch, url, data)
    // ToDo: Check result status to insure it passed.
    yield put(actions.updateCommentSuccess({id: id}))
  } catch (e) {
    captureException(e)
    yield put(actions.updateCommentFail({id: id, error: e}))
  }
}

function* deleteComment({payload: data}) {
  const {page_url, update_url, page_id} = moduleConfig
  
  const [group, slug] = page_url.split('/').slice(1) //?
  
  const {id} = data
  
  const url = update_url
    .replace(/str:group/, group)
    .replace(/int:page_id/, page_id)
    .replace(/int:comment_id/, id)
  
  const axios = get_axios()
  try {
    const result = yield call(axios.delete, url, data)
    // ToDo: Check result status to insure it passed.
    yield put(actions.deleteCommentSuccess({id: id}))
  } catch (e) {
    captureException(e)
    yield put(actions.deleteCommentFail({id: id, error: e}))
  }
}


export default function* rootSaga() {
  yield all([
    fork(channelsConnectionManager),
    fork(getComments),
    
    yield takeEvery(types.GET_COMMENTS, getComments),
    yield takeLatest(types.REFRESH_COMMENTS, getComments),
    yield takeLatest(types.COMMENT_ADDED, getComments),
    yield takeLatest(types.COMMENT_UPDATED, getComments),
    yield takeEvery(types.ADD_NEW_TT_COMMENT, addComment),
    yield takeEvery(types.UPDATE_COMMENT, updateComment),
    yield takeEvery(types.DELETE_COMMENT, deleteComment),
  ])
}