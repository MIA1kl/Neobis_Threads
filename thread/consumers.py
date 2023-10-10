# your_app_name/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ThreadConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def update_thread(self, event):
        thread_data = event['data']

        # Отправка данных обновления в WebSocket
        await self.send(text_data=json.dumps({
            'type': 'update_thread',
            'data': thread_data,
        }))

        # Печать в консоль бэкэнда для отслеживания
        print(f"Sent update to WebSocket clients: {thread_data}")
