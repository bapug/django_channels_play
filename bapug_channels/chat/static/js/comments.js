
function init_comments(groupName, slugName) {

  const submitBtn = $('#chat-message-submit')
  const messageInputDom = $('#chat-message-input')
  const getMsg = () => {
    const val = messageInputDom.val()
    console.log(`new val is ${val}`)
    messageInputDom.val('')
    return val
  }

  let connected = false

  const setupSocket = () => {
    console.log('Setting up socket connection')
    let chatSocket = new WebSocket(
      `ws://${window.location.host}/ws/comments/${groupName}/${slugName}/`)

    chatSocket.onopen = function(e) {
      connected = true
      console.log('Connection established')

      submitBtn.on('click', function(e) {
        chatSocket.send(JSON.stringify({
          'message': getMsg()
        }))
      })
    }

    chatSocket.onmessage = function(e) {
      let data = JSON.parse(e.data)
      console.dir(data)
      if ('message' in data) {
        let message = data['message']
        document.querySelector('#chat-log').value += (message + '\n')
      } else {
        document.querySelector('#chat-log').value += (e.data + '\n')
      }
    }

    chatSocket.onclose = function(e) {
      console.error('Chat socket closed unexpectedly')
      connected = false
      submitBtn.off('click')
    }

  }

  document.querySelector('#chat-message-input').focus()
  document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
      document.querySelector('#chat-message-submit').click()
    }
  }

  messageInputDom.val('')

  setupSocket()
  setInterval(function() {
    if (!connected) {
      console.log('Reconnecting')
      setupSocket()
    }
  }, 3000)
  
}
