import json
from channels.generic.websocket import AsyncWebsocketConsumer
from accounts.models import CustomUser
from rest_framework_simplejwt.tokens import AccessToken
from .utils import save_message, room_name_generator, get_message_history,get_notification_history
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from .message_senders import send_message,send_notification
from .notification_manager import received_notification_manager

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.slug = self.scope["url_route"]["kwargs"]["room_id"]
        self.user_id = await get_user(self.scope)

        if self.user_id == False:
            await self.close()

        self.room_name = room_name_generator(self.slug, "chat")
        print(self.room_name)
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        self.online_status = True

        await self.accept()
        data = {"event_name": "connect", "data": "connected"}
        await self.send(text_data=json.dumps(data))

        messages = await get_message_history(self.user_id, self.room_name)
        await send_message(self.room_name,'message_history', messages)

    async def disconnect(self, close_code):
        self.channel_layer.group_discard(self.room_name, self.channel_name)
        print("===========Chat Disconnected============================")

    async def receive(self, text_data=None):
        new_message = save_message(self.user_id, text_data, self.room_name)
        await self.channel_layer.group_send(
            self.room_name, {"type": "new_message", "message": new_message}
        )

    async def send_message(self, data):
        await self.send(text_data=json.dumps(data))

    async def message_history(self, event):
        data = {"event_name": "message_history", "message": event["message"]}
        await self.send(text_data=json.dumps(data))

    async def new_message(self, event):
        data = {"event_name": "new_message", "message": event["message"]}
        await self.send(text_data=json.dumps(data))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
  
        self.user_id = await get_user(self.scope)
        if self.user_id == False:
            await self.close()

        self.group_name = room_name_generator(self.user_id, "notification")
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print('notify connected')
        data = {"event_name": "connect", "data": "notify server connected"}
        await self.send(text_data=json.dumps(data))

        notifications = await get_notification_history(self.user_id, self.group_name)
        await send_notification( notifications,'notification_history',self.group_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

        print('===============Notification disconnected================")')

    async def receive(self, text_data):
        data = json.loads(text_data)
        await received_notification_manager(self.user_id,data)
   

    async def send_notification(self, event):
        data = {"event_name": event["event_name"], "message": event["message"]}
        await self.send(text_data=json.dumps({"message": data}))



# class VideoChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
  
#         self.user_id = await get_user(self.scope)
#         if self.user_id == False:
#             await self.close()

#         self.group_name = room_name_generator(self.user_id, "video_chat")
#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()
#         print('SIGNALLING SERVER CONNECTED')
#         data = {"event_name": "connect", "data": "SIGNALLING server connected"}
#         await self.send(text_data=json.dumps(data))

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)

#         print('===============SIGNALLING SERVER disconnected================")')

#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         print('video signal received===>>',data)


async def get_user(scope):
    # Retrieve user from JWT token
    token = scope["query_string"].decode().split("=")[1]

    try:
        access_token = AccessToken(token)
        user_id = access_token["user_id"]
        if user_id is not None:
            return user_id
    except Exception as e:

        return False
