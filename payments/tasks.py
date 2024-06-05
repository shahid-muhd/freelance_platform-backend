from celery import shared_task
from django.utils import timezone
from payments.models import Subscription
import logging


@shared_task
def check_subscription_expiry():
    # current_date = timezone.now()

    expired_subscriptions = Subscription.objects.filter(is_active=True)
    for subscription in expired_subscriptions:
        subscription.is_active = False
        subscription.save()



# @shared_task
# def send_subscription_email(user_email, subject, message):
#     print('subscription expired')