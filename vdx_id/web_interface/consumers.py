import json
import logging
from time import gmtime, strftime
from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('vdx_id.%s' % __name__)


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope['user'].is_anonymous:
            self.close()
            return

        await self.channel_layer.group_add(
            'notifications',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            'notifications',
            self.channel_name
        )

    # Receive text from room group
    async def notification(self, event):
        text = event['text']
        style = event.get('style', 'info')
        lane = event.get('lane', 'internal')

        # Send text to WebSocket
        await self.send(
            text_data=json.dumps({
                'text': text, 'style': style, 'lane': lane
            })
        )


class MapUpdateConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            'map_update',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            'map_update',
            self.channel_name
        )

    # Receive text from room group
    async def map_update(self, event):
        flows = event['flows']

        # Send text to WebSocket
        await self.send(
            text_data=json.dumps({
                'flows': flows
            })
        )
