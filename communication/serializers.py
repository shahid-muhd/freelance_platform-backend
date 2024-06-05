import json
from rest_framework import serializers

from accounts.models import CustomUser
from datetime import datetime
from django.utils import timezone

def convert_epoch_to_datetime(epoch_time):
  today = timezone.now().date()
  return timezone.make_aware(datetime.fromtimestamp(epoch_time)).strftime("%I:%M %p on %B %d, %Y")


class NotificationSerializer:
    def serialize(self,query_data):
        
        notifications=[]
        unseen_notification_count = 0
    
        for item in query_data:
            notifications.append(
                {
                    "id": str(item.id),
                    "title": item.title,
                    "description": item.description,
                    'read_status':item.read_status,
                    'type':item.type
                }
            )
            if item.read_status == False:
                unseen_notification_count += 1
  
        return notifications

class MessageSerializer:
    def serialize(self, query_data):
        messages = []
        unseen_message_count = 0
        for item in query_data:
            messages.append(
                {
                    "id": str(item.id),
                    "text": item.text,
                    "sender": item.sender,
                    "receiver": item.receiver,
                    "created_time":str( convert_epoch_to_datetime(item.created_time)),
                    "room_name": item.room_name,
                    "status": item.status,
                }
            )
            if item.status == "unseen":
                unseen_message_count += 1
        # messages.append({"unseen_count": unseen_message_count})
        return messages


class ExchangerPrimitiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "first_name", "last_name", "profile_image")
