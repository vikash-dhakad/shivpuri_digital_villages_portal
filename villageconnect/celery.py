"""Celery application for VillageConnect background tasks."""

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'villageconnect.settings')

app = Celery('villageconnect')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
