from django.urls import re_path

from communication import consumers

ws_urlpatterns = [
    re_path(r"ws/chat/(?P<room_id>[\w-]+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/notifications/$", consumers.NotificationConsumer.as_asgi()),
    # re_path(r"ws/video_chat/$", consumers.VideoChatConsumer.as_asgi()),
]
