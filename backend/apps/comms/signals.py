"""
Django signals for marketing reminders
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='calendar.Appointment')
def appointment_created_or_updated(sender, instance, created, **kwargs):
    """Handle appointment create/update to trigger reminders"""
    from .models import Reminder, ReminderJob
    from .tasks import is_quiet_hours
    
    # Determine reminder type
    if created:
        reminder_type = 'PREBOOK_CREATE'
    else:
        reminder_type = 'PREBOOK_UPDATE'
    
    # Find applicable reminders
    reminders = Reminder.objects.filter(
        organization=instance.patient.organization,
        enabled=True,
        type=reminder_type
    )
    
    for reminder in reminders:
        # Check if link_service matches (if specified)
        if reminder.link_service and hasattr(instance, 'service'):
            if instance.service != reminder.link_service:
                continue
        
        # Check if job already exists (avoid duplicates for updates)
        existing = ReminderJob.objects.filter(
            reminder=reminder,
            appointment=instance,
            status='queued'
        ).exists()
        
        if existing:
            continue
        
        # Calculate scheduled time
        scheduled_at = timezone.now() + timedelta(
            days=reminder.offset_days,
            hours=reminder.offset_hours
        )
        
        # Adjust for quiet hours
        if is_quiet_hours(scheduled_at):
            scheduled_at = scheduled_at.replace(hour=8, minute=0, second=0, microsecond=0)
            if scheduled_at < timezone.now():
                scheduled_at += timedelta(days=1)
        
        # Create reminder job
        ReminderJob.objects.create(
            reminder=reminder,
            patient=instance.patient,
            appointment=instance,
            scheduled_at=scheduled_at,
            status='queued'
        )
        logger.info(f"Created {reminder_type} job for appointment {instance.id}")


@receiver(post_delete, sender='calendar.Appointment')
def appointment_deleted(sender, instance, **kwargs):
    """Handle appointment deletion to trigger reminder"""
    from .models import Reminder, ReminderJob
    from .tasks import is_quiet_hours
    
    # Cancel existing queued jobs for this appointment
    ReminderJob.objects.filter(
        appointment=instance,
        status='queued'
    ).update(status='skipped', error='Appointment deleted')
    
    # Find PREBOOK_DELETE reminders
    reminders = Reminder.objects.filter(
        organization=instance.patient.organization,
        enabled=True,
        type='PREBOOK_DELETE'
    )
    
    for reminder in reminders:
        # Calculate scheduled time
        scheduled_at = timezone.now() + timedelta(
            hours=reminder.offset_hours
        )
        
        # Adjust for quiet hours
        if is_quiet_hours(scheduled_at):
            scheduled_at = scheduled_at.replace(hour=8, minute=0, second=0, microsecond=0)
            if scheduled_at < timezone.now():
                scheduled_at += timedelta(days=1)
        
        # Create reminder job
        ReminderJob.objects.create(
            reminder=reminder,
            patient=instance.patient,
            appointment=instance,
            scheduled_at=scheduled_at,
            status='queued'
        )
        logger.info(f"Created PREBOOK_DELETE job for appointment {instance.id}")


def trigger_prebook_cancel_reminder(appointment):
    """Trigger PREBOOK_CANCEL reminder when appointment is cancelled"""
    from .models import Reminder, ReminderJob
    from .tasks import is_quiet_hours
    
    # Cancel existing queued jobs for this appointment (except cancel type)
    ReminderJob.objects.filter(
        appointment=appointment,
        status='queued'
    ).exclude(reminder__type='PREBOOK_CANCEL').update(
        status='skipped',
        error='Appointment cancelled'
    )
    
    # Find PREBOOK_CANCEL reminders
    reminders = Reminder.objects.filter(
        organization=appointment.patient.organization,
        enabled=True,
        type='PREBOOK_CANCEL'
    )
    
    for reminder in reminders:
        # Check if job already exists
        existing = ReminderJob.objects.filter(
            reminder=reminder,
            appointment=appointment
        ).exists()
        
        if existing:
            continue
        
        # Calculate scheduled time
        scheduled_at = timezone.now() + timedelta(
            hours=reminder.offset_hours
        )
        
        # Adjust for quiet hours
        if is_quiet_hours(scheduled_at):
            scheduled_at = scheduled_at.replace(hour=8, minute=0, second=0, microsecond=0)
            if scheduled_at < timezone.now():
                scheduled_at += timedelta(days=1)
        
        # Create reminder job
        ReminderJob.objects.create(
            reminder=reminder,
            patient=appointment.patient,
            appointment=appointment,
            scheduled_at=scheduled_at,
            status='queued'
        )
        logger.info(f"Created PREBOOK_CANCEL job for appointment {appointment.id}")


def trigger_online_confirm_reminder(appointment):
    """Trigger ONLINE_CONFIRM reminder when patient books online"""
    from .models import Reminder, ReminderJob
    from .tasks import is_quiet_hours
    
    # Find ONLINE_CONFIRM reminders
    reminders = Reminder.objects.filter(
        organization=appointment.patient.organization,
        enabled=True,
        type='ONLINE_CONFIRM'
    )
    
    for reminder in reminders:
        # Check if job already exists
        existing = ReminderJob.objects.filter(
            reminder=reminder,
            appointment=appointment
        ).exists()
        
        if existing:
            continue
        
        # Calculate scheduled time (usually immediate or within minutes)
        scheduled_at = timezone.now() + timedelta(
            hours=reminder.offset_hours
        )
        
        # For online confirmations, send even in quiet hours (transactional)
        
        # Create reminder job
        ReminderJob.objects.create(
            reminder=reminder,
            patient=appointment.patient,
            appointment=appointment,
            scheduled_at=scheduled_at,
            status='queued'
        )
        logger.info(f"Created ONLINE_CONFIRM job for appointment {appointment.id}")

