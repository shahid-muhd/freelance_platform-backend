from mongoengine import Document, fields
import datetime

# Create your models here.


from django.db import models


class Messages(Document):
    sender = fields.IntField(required=True)
    receiver = fields.IntField(required=True)
    text = fields.StringField(required=True)
    created_time = fields.IntField(
        required=True,
    )
    room_name = fields.StringField(required=True)
    status = fields.StringField(default="unseen")

    def save(self, *args, **kwargs):
        if not self.created_time:
            self.created_time = int(datetime.datetime.now().timestamp())
        super().save(*args, **kwargs)



class UserNotifications(Document):
    user=fields.IntField(required=True)
    title=fields.StringField(required=True)
    description=fields.StringField(required=True)
    read_status=fields.BooleanField(default=False)
    type=fields.StringField()
    group_name = fields.StringField(required=True)


class Room(Document):
    sender = fields.IntField(required=True)
    receiver = fields.IntField(required=True)
    room_name = fields.StringField()

