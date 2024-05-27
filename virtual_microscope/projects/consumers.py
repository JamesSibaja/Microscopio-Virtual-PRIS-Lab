import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtual_microscope.settings')

import json
import django
django.setup()
from .models import Message, User
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.project_group_name = f'project_{self.project_id}'

        await self.channel_layer.group_add(
            self.project_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.project_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = data['user']

        Message.objects.create(
            project_id=self.project_id,
            user_id=user,
            contenido=message
        )

        await self.channel_layer.group_send(
            self.project_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'user': user
            }
        )

    async def chat_message(self, event):
        message = event['message']
        user = event['user']

        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'username':User.objects.get(id= int(user)).username,
            'fecha': datetime.now().strftime("%I:%M %p")
        }))