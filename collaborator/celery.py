from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collaborator.settings')

app = Celery('collaborator')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

@app.task
def check_subscription_expiry():
    from payments.models import Subscription

    subscriptions = Subscription.objects.filter(is_active=True)
    for subscription in subscriptions:
        subscription.is_active = False
        subscription.save()

    print('Subscriptions deactivated successfully.')
