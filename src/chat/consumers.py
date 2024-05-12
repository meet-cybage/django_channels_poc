import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import ChatMesssage


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]

        # Join room group
        # async_to_sync(self.channel_layer.group_add)(
        #     self.room_name, self.channel_name
        # )

        await self.channel_layer.group_add(self.room_name, self.channel_name)

        await self.accept()
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        sender = text_data_json["logged_user_id"]
        chat_message = await self.create_chat_record(sender, text_data_json)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_name, {"type": "chat.message", "message": chat_message.get("message"), "room_id":chat_message.get("room_id"), "sender": sender}
        )

    @database_sync_to_async
    def create_chat_record(self, sender, data):
        obj = ChatMesssage.objects.create_chat_message(sender, data)
        return {"message": obj.message, "room_id": obj.chat_room.id}    
    
    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        room_id = event["room_id"]
        sender = event["sender"]
        # Send message to WebSocket
    
        await self.send(text_data=json.dumps({"message": message, "sender": sender, "room_id": room_id}))