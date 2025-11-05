"""
Celery tasks for Telegram Bot
"""
from celery import shared_task
from datetime import datetime, timedelta
from django.utils import timezone
from apps.calendar.models import Appointment
from apps.telegram_bot.models import PatientTelegramLink, BotBroadcast, BotDocument
from apps.telegram_bot.services.segmentation import PatientSegmentation
from apps.telegram_bot.services.document_generator import DocumentGenerator
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_appointment_reminders():
    """
    Send appointment reminders via Telegram bot
    - D-1: 24 hours before
    - H-3: 3 hours before
    - H-1: 1 hour before
    """
    now = timezone.now()
    
    # D-1 reminders (tomorrow at this time)
    tomorrow = now + timedelta(days=1)
    d1_start = tomorrow - timedelta(minutes=15)
    d1_end = tomorrow + timedelta(minutes=15)
    
    d1_appointments = Appointment.objects.filter(
        date=tomorrow.date(),
        time_from__gte=d1_start.time(),
        time_from__lte=d1_end.time(),
        status='scheduled'
    ).select_related('patient__telegram_link')
    
    # H-3 reminders (3 hours from now)
    h3_time = now + timedelta(hours=3)
    h3_start = h3_time - timedelta(minutes=15)
    h3_end = h3_time + timedelta(minutes=15)
    
    h3_appointments = Appointment.objects.filter(
        date=h3_time.date(),
        time_from__gte=h3_start.time(),
        time_from__lte=h3_end.time(),
        status='scheduled'
    ).select_related('patient__telegram_link')
    
    # H-1 reminders (1 hour from now)
    h1_time = now + timedelta(hours=1)
    h1_start = h1_time - timedelta(minutes=15)
    h1_end = h1_time + timedelta(minutes=15)
    
    h1_appointments = Appointment.objects.filter(
        date=h1_time.date(),
        time_from__gte=h1_start.time(),
        time_from__lte=h1_end.time(),
        status='scheduled'
    ).select_related('patient__telegram_link')
    
    # Send reminders (this would integrate with actual bot sending mechanism)
    # For now, we'll just log
    for apt in d1_appointments:
        if hasattr(apt.patient, 'telegram_link') and apt.patient.telegram_link.is_active:
            logger.info(f"D-1 Reminder: {apt.patient.full_name} - {apt.date} {apt.time_from}")
            # TODO: Send actual Telegram message
    
    for apt in h3_appointments:
        if hasattr(apt.patient, 'telegram_link') and apt.patient.telegram_link.is_active:
            logger.info(f"H-3 Reminder: {apt.patient.full_name} - {apt.date} {apt.time_from}")
            # TODO: Send actual Telegram message
    
    for apt in h1_appointments:
        if hasattr(apt.patient, 'telegram_link') and apt.patient.telegram_link.is_active:
            logger.info(f"H-1 Reminder: {apt.patient.full_name} - {apt.date} {apt.time_from}")
            # TODO: Send actual Telegram message
    
    return {
        'd1_sent': d1_appointments.count(),
        'h3_sent': h3_appointments.count(),
        'h1_sent': h1_appointments.count()
    }


@shared_task
def send_arrived_check():
    """
    Send "Have you arrived?" check 5 minutes after appointment time
    """
    now = timezone.now()
    check_time = now - timedelta(minutes=5)
    
    appointments = Appointment.objects.filter(
        date=check_time.date(),
        time_from__lte=check_time.time(),
        status='scheduled'
    ).select_related('patient__telegram_link')
    
    for apt in appointments:
        if hasattr(apt.patient, 'telegram_link') and apt.patient.telegram_link.is_active:
            logger.info(f"Arrived Check: {apt.patient.full_name} - {apt.date} {apt.time_from}")
            # TODO: Send actual Telegram message with buttons: "Arrived" / "Cancel"
    
    return appointments.count()


@shared_task
def send_feedback_request():
    """
    Send NPS feedback request 2 hours after visit completion
    """
    from apps.visits.models import Visit
    
    now = timezone.now()
    feedback_time = now - timedelta(hours=2)
    
    # Get completed visits from 2 hours ago
    visits = Visit.objects.filter(
        visit_date=feedback_time.date(),
        status='completed',
        # Check if feedback not already collected
    ).select_related('patient__telegram_link').exclude(
        appointment__bot_feedbacks__isnull=False
    )
    
    for visit in visits:
        if hasattr(visit.patient, 'telegram_link') and visit.patient.telegram_link.is_active:
            logger.info(f"Feedback Request: {visit.patient.full_name} - {visit.visit_date}")
            # TODO: Send actual Telegram message with NPS buttons 0-10
    
    return visits.count()


@shared_task
def process_broadcast(broadcast_id):
    """
    Process broadcast: filter patients and send messages
    """
    try:
        broadcast = BotBroadcast.objects.get(id=broadcast_id)
    except BotBroadcast.DoesNotExist:
        logger.error(f"Broadcast {broadcast_id} not found")
        return
    
    # Update status to running
    broadcast.status = 'running'
    broadcast.started_at = timezone.now()
    broadcast.save()
    
    # Filter patients
    patients = PatientSegmentation.filter_patients(
        broadcast.organization,
        broadcast.segment_filters_json
    )
    
    broadcast.total_recipients = patients.count()
    broadcast.save()
    
    # Send messages to each patient
    sent_count = 0
    failed_count = 0
    
    for patient in patients:
        try:
            if not hasattr(patient, 'telegram_link') or not patient.telegram_link.is_active:
                continue
            
            # Get message text based on patient's language
            language = patient.telegram_link.language
            message_text = broadcast.text_ru if language == 'ru' else (broadcast.text_kk or broadcast.text_ru)
            
            # TODO: Send actual Telegram message
            logger.info(f"Broadcast to {patient.full_name}: {message_text[:50]}...")
            
            sent_count += 1
            
        except Exception as e:
            logger.error(f"Failed to send broadcast to {patient.full_name}: {str(e)}")
            failed_count += 1
    
    # Update broadcast statistics
    broadcast.sent_count = sent_count
    broadcast.failed_count = failed_count
    broadcast.delivered_count = sent_count  # Will be updated by webhook
    broadcast.status = 'completed'
    broadcast.completed_at = timezone.now()
    broadcast.save()
    
    return {
        'broadcast_id': str(broadcast_id),
        'total_recipients': broadcast.total_recipients,
        'sent': sent_count,
        'failed': failed_count
    }


@shared_task
def cleanup_expired_documents():
    """
    Mark expired bot documents as expired
    """
    count = DocumentGenerator.cleanup_expired_documents()
    logger.info(f"Marked {count} documents as expired")
    return count


@shared_task
def sync_patient_marketing_consent():
    """
    Sync marketing consent from telegram_link to patient
    """
    links = PatientTelegramLink.objects.filter(is_active=True)
    
    updated = 0
    for link in links:
        if link.consents_json.get('marketing'):
            if not link.patient.is_marketing_opt_in:
                link.patient.is_marketing_opt_in = True
                link.patient.save()
                updated += 1
    
    return updated

