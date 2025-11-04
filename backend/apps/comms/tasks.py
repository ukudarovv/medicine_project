from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_appointment_reminder(appointment_id, hours_before):
    """Send appointment reminder"""
    from apps.calendar.models import Appointment
    from .models import MessageLog, Template
    from .providers import get_sms_provider
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check if already sent
        existing = MessageLog.objects.filter(
            appointment=appointment,
            template_key=f'appointment_reminder_{hours_before}h'
        ).exists()
        
        if existing:
            return
        
        # Get template
        template = Template.objects.filter(
            channel='sms',
            key=f'appointment_reminder_{hours_before}h'
        ).first()
        
        if not template:
            logger.warning(f"Template not found for {hours_before}h reminder")
            return
        
        # Format message
        text = template.body.format(
            patient_name=appointment.patient.full_name,
            doctor_name=appointment.employee.full_name,
            date=appointment.start_datetime.strftime('%d.%m.%Y'),
            time=appointment.start_datetime.strftime('%H:%M')
        )
        
        # Send SMS
        provider = get_sms_provider()
        result = provider.send_sms(appointment.patient.phone, text)
        
        # Log
        MessageLog.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            channel='sms',
            template_key=template.key,
            text=text,
            cost=result.get('cost', 0),
            status='sent' if result.get('success') else 'failed'
        )
        
    except Exception as e:
        logger.error(f"Error sending reminder: {e}")


@shared_task
def send_appointment_reminders(hours_before=24):
    """Check and send appointment reminders"""
    from apps.calendar.models import Appointment
    from django.utils import timezone
    
    target_time = timezone.now() + timedelta(hours=hours_before)
    time_window = timedelta(minutes=30)
    
    appointments = Appointment.objects.filter(
        start_datetime__gte=target_time - time_window,
        start_datetime__lte=target_time + time_window,
        status__in=['booked', 'confirmed']
    )
    
    for appointment in appointments:
        send_appointment_reminder.delay(appointment.id, hours_before)

