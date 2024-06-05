from .models import Messages,UserNotifications
from .serializers import MessageSerializer,NotificationSerializer
import json
from django.db.models import Q
import datetime
from projects.models import Proposals, Project
from accounts.models import CustomUser
from .serializers import ExchangerPrimitiveSerializer
from asgiref.sync import sync_to_async
from asgiref.sync import sync_to_async

def get_exchangers(current_user):
    projects = Project.objects.filter(client_id=current_user).values_list(
        "id", flat=True
    )
    applicants = list(
        Proposals.objects.filter(project_id__in=projects)
        .values_list("applicant", flat=True)
        .distinct()
    )

    proposal = Proposals.objects.filter(applicant_id=current_user).values_list(
        "project", flat=True
    )
    clients = list(
        Project.objects.filter(id__in=proposal)
        .exclude(client_id__in=applicants)
        .values_list("client", flat=True)
    )

    exchangers_id = applicants + clients

    exchangers = list(
        CustomUser.objects.filter(id__in=exchangers_id).values(
            "id", "first_name", "last_name", "profile_image"
        )
    )

    return exchangers


def unseen_messages_count(current_user, query_params=None):
    count = Messages.objects(receiver=current_user, status="unseen").count()

    return count


async def get_message_history(current_user_id,room_name):
    messages = Messages.objects(room_name=room_name)
    message_serializer = MessageSerializer()
    messages = message_serializer.serialize(messages)

    return messages

async def get_notification_history(current_user_id,group_name):
    notifications = UserNotifications.objects(group_name=group_name)
    notification_serializer = NotificationSerializer()
    notifications = notification_serializer.serialize(notifications)

    return notifications


def save_message(user_id, message,room_name):
    message = json.loads(message)
    message["sender"] = user_id
    message['room_name']=room_name
    new_message = Messages(**message)
    new_message.save()

    new_message = Messages.objects.filter(id=new_message.id)

    message_serializer = MessageSerializer()
    message = message_serializer.serialize(new_message)


    return message


def room_name_generator(id,type):
    return f"{type}_" + "".join(sorted(str(id)))



