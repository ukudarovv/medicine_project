"""
Celery configuration
"""
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('medicine_erp')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'send-appointment-reminders-24h': {
        'task': 'apps.comms.tasks.send_appointment_reminders',
        'schedule': crontab(hour='9', minute='0'),  # Daily at 9:00 AM
        'kwargs': {'hours_before': 24},
    },
    'send-appointment-reminders-3h': {
        'task': 'apps.comms.tasks.send_appointment_reminders',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'kwargs': {'hours_before': 3},
    },
    'send-appointment-reminders-1h': {
        'task': 'apps.comms.tasks.send_appointment_reminders',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'kwargs': {'hours_before': 1},
    },
}

