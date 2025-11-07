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
    # Legacy appointment reminders
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
    # Marketing reminder tasks
    'generate-reminder-jobs': {
        'task': 'apps.comms.tasks.generate_reminder_jobs',
        'schedule': crontab(hour='1', minute='0'),  # Daily at 1:00 AM
    },
    'process-reminder-queue': {
        'task': 'apps.comms.tasks.process_reminder_queue',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    'fetch-delivery-statuses': {
        'task': 'apps.comms.tasks.fetch_delivery_statuses',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'calculate-conversions': {
        'task': 'apps.comms.tasks.calculate_conversions',
        'schedule': crontab(hour='2', minute='0'),  # Daily at 2:00 AM
    },
    # Campaign tasks
    'run-scheduled-campaigns': {
        'task': 'apps.comms.tasks.run_scheduled_campaigns',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    # Telegram Bot tasks - DISABLED (module not in container)
    # 'bot-send-appointment-reminders': {
    #     'task': 'apps.telegram_bot.tasks.send_appointment_reminders',
    #     'schedule': crontab(minute='*/15'),  # Every 15 minutes
    # },
    # 'bot-send-arrived-check': {
    #     'task': 'apps.telegram_bot.tasks.send_arrived_check',
    #     'schedule': crontab(minute='*/5'),  # Every 5 minutes
    # },
    # 'bot-send-feedback-request': {
    #     'task': 'apps.telegram_bot.tasks.send_feedback_request',
    #     'schedule': crontab(minute='*/30'),  # Every 30 minutes
    # },
    # 'bot-cleanup-expired-documents': {
    #     'task': 'apps.telegram_bot.tasks.cleanup_expired_documents',
    #     'schedule': crontab(hour='*/6', minute='0'),  # Every 6 hours
    # },
}

