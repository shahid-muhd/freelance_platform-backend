from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'communication'
    def ready(self):
        from . import message_senders
        from . import notification_manager
