import logging
from json import JSONDecodeError
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
import json

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"Connecting...")
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Broadcast to group that a client has joined
    # "ed has joined the channel" -- etc.
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
        except JSONDecodeError as e:
            message = text_data

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        group = self.scope['url_route']['kwargs']['group']
        self.notify_group = group

        logger.debug(f"Connection on {group} to {self.channel_name}")
        logger.debug(f"Notify Group: {self.notify_group}")

        # Join room group
        await self.channel_layer.group_add(
            self.notify_group,
            self.channel_name
        )

        await self.accept()

        await self.welcomeMessage()

    async def disconnect(self, close_code):
        # Leave room group
        logger.debug(f"Closing the channel with code {close_code}")
        await self.channel_layer.group_discard(
            self.notify_group,
            self.channel_name
        )

    async def welcomeMessage(self):
        """ Send a welcome message to new client """

        await self.send(text_data=json.dumps({
            'action': 'actionGroupConnected',
            'payload': {'last_event': 'yesterday'}
        }))

    async def receive(self, text_data):
        """
        Process message received from wss client

        There are not a lot of reason for the client to
        talk to the server, but perhaps they could  ask
        a question??

        :param text_data:
        :return:
        """

        print(f"Incoming message from {self.channel_name}: {text_data}")

        try:
            logger.debug(f"parsing {text_data}")
            data = json.loads(text_data)

            action = data.get('action')

            if action == 'refreshOldComments':
                await self.send(text_data=json.dumps({
                    'action': 'refreshOldComments',
                    'payload': {'last_update': '5 minutes ago'}
                }))
        except JSONDecodeError as e:
            pass

    async def comment_event(self, event):
        """
        Broadcast an event to all clients
        Event action maps to a redux action name
        Payload is the data for the action
        :param event:
        :return:
        """

        logger.debug(f"comment.event Event:{event}")

        await self.send(text_data=json.dumps({
            'action': event.get("action", 'unknownAction'),
            'payload': event.get("payload", {})
        }))


class CommentSyncHandler:
    """
    Synchronous versions that can be called from Django code
    """

    @staticmethod
    def comment_updated(group_name=None, comment=None):
        channel_layer = get_channel_layer()
        logger.debug("Sending comment updated message")
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "comment.event",
                "action": "commentUpdated",
                "payload": {
                    'id': comment.id,
                    'last_updated': comment.updated_on.isoformat(),
                    'updated': True,
                }
            }
        )

    @staticmethod
    def comment_added(group_name=None, comment=None):
        channel_layer = get_channel_layer()
        logger.debug("Sending comment added message")
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "comment.event",
                "action": "commentAdded",
                "payload": {
                    'id': comment.id,
                    'last_updated': comment.updated_on.isoformat(),
                    'created': True,
                }
            }
        )

    @staticmethod
    def comment_deleted(group_name=None, id=None):
        channel_layer = get_channel_layer()
        logger.debug("Sending comment deleted message")
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "comment.event",
                "action": "commentDeleted",
                "payload": {
                    'id': id,
                }
            }
        )
