# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.contrib.auth.models import AnonymousUser

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
     self.user = self.scope['user']
    
     if isinstance(self.user, AnonymousUser):
        await self.close()
        return

    # Each user joins their own personal room
     self.room_group_name = f'call_{self.user.id}'

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

    async def receive(self, text_data):
     data = json.loads(text_data)
     data['sender'] = self.user.username
     
     target_id = data.get('target_id')  # The intended recipient
     if not target_id:
        return

     await self.channel_layer.group_send(
        f'call_{target_id}',  # Target user's room
        {
            'type': 'call_signal',
            'data': data
        }
    )


    async def call_signal(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['data']))