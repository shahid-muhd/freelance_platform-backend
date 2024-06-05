from django.dispatch import receiver
from .models import UserNotifications
from django.db.models.signals import post_save
from projects.models import Proposals, Project
from django.core.mail import send_mail
from accounts.models import CustomUser
from projects.signals import proposal_acceptance_signal
from .signals import post_notification_signal
from .serializers import NotificationSerializer
from .utils import room_name_generator
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async


@receiver(post_save, sender=Proposals)
def proposal_signal_receiver(sender, instance: Proposals, created, **kwargs):
    print("in signal receiver")
    project = Project.objects.values("title", "client_id", "client__email").get(
        id=instance.project_id
    )
    freelancer = CustomUser.objects.values("first_name", "last_name", "email").get(
        id=instance.applicant_id
    )
    project_title = project["title"]

    messages = {
        "proposal_received_email": f"You have received a proposal for your project : {project_title}.Check app noifications for more information.",
        "proposal_receieved_notification": f"You have received a proposal for your project : {project_title} from {freelancer['first_name']} {freelancer['last_name']}.",
        "proposal_acceptance_notification": f"""Congratulations!! Your proposal for the project "{project_title}" has been accepted. """,
    }
    if created:

        email_receiver = project["client__email"]
        notification_receiver = project["client_id"]
        email_subject = "Received new proposal"
        email_Content = messages["proposal_received_email"]
        notification_content = messages["proposal_receieved_notification"]

    else:
        email_receiver = freelancer["email"]
        notification_receiver = instance.applicant_id
        email_subject='Proposal Accepted'
        email_Content = messages["proposal_acceptance_notification"]
        notification_content = messages["proposal_acceptance_notification"]

    proposal_email_notifier(email_subject, email_receiver, email_Content)

    group_name = room_name_generator(notification_receiver, "notification")
    create_app_notification(
        user=notification_receiver,
        title=email_subject,
        description=notification_content,
        type="proposal",
        group_name=group_name,
    )


def proposal_email_notifier(subject, email, message):

    send_mail(
        subject=f"Loomix Jobs {subject}",
        message=message,
        from_email="shahid04m@gmail.com",
        recipient_list=[email],
        fail_silently=False,
    )


def create_app_notification(**details):
    print("in noty creator")
    try:
        new_notification = UserNotifications(**details)
        type = new_notification.type
        new_notification.save()
        user = new_notification.user
        new_notification = UserNotifications.objects(id=new_notification.id)
        notification_serializer = NotificationSerializer()
        new_notification = notification_serializer.serialize(new_notification)

        post_notification_signal.send(
            sender="create_app_notification",
            notification=new_notification,
            user=user,
            type=type,
        )

    except Exception as e:
        print(e)


@database_sync_to_async
def received_notification_manager(currentUserId, notification):
    event = notification["event_name"]
    message = notification["message"]
    if event == "video_chat_room_id":
        exchanger = message["exchanger"]
        group_name = room_name_generator(exchanger, "notification")

        caller = CustomUser.objects.get(id=currentUserId)
        create_app_notification(
            user=exchanger,
            title=f"{caller.first_name} {caller.last_name} wants to call you.",
            description=message["roomID"],
            type="call",
            group_name=group_name,
        )
