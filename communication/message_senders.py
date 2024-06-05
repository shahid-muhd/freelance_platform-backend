from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from .models import UserNotifications
from django.dispatch import receiver
from .signals import post_notification_signal
from asgiref.sync import async_to_sync
from .utils import room_name_generator


async def send_message(room_name, message_type, message):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        room_name,
        {
            "type": message_type,
            "message": message,
        },
    )


@receiver(post_notification_signal)
def send_notification_receiver(sender=None, **details):
    print('signal working')
    type=details.get('type')
    notification = details.get("notification")
    user=details.get('user')
    async_to_sync(send_notification)(notification,type,None,user)


async def send_notification(notification,type,group_name=None,user=None):
    if group_name is None and user is not None:
        group_name = room_name_generator(user, "notification")


    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        group_name, {"type": "send_notification", "message": notification,'event_name':type}
    )
