from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.db.models import Q, F
from datetime import timedelta, datetime, time
import logging
import hashlib

logger = logging.getLogger(__name__)


def is_quiet_hours(dt=None):
    """Check if current time is in quiet hours (22:00 - 08:00)"""
    if dt is None:
        dt = timezone.now()
    
    local_time = dt.time()
    quiet_start = time(22, 0)  # 22:00
    quiet_end = time(8, 0)     # 08:00
    
    if quiet_start > quiet_end:
        # Crosses midnight
        return local_time >= quiet_start or local_time < quiet_end
    else:
        return quiet_start <= local_time < quiet_end


def apply_placeholders(body, patient, visit=None, appointment=None):
    """Apply placeholders to message body (wrapper for utils function)"""
    from .utils import apply_placeholders_to_message
    return apply_placeholders_to_message(body, patient, visit, appointment)


def check_antispam(patient, body_hash, window_hours=24):
    """Check if same message was sent to patient within window"""
    from .models import ContactLog
    
    cutoff = timezone.now() - timedelta(hours=window_hours)
    return ContactLog.objects.filter(
        patient=patient,
        body_hash=body_hash,
        created_at__gte=cutoff
    ).exists()


# ==================== Marketing Tasks ====================


@shared_task
def generate_reminder_jobs():
    """Generate reminder jobs for AFTER_VISIT, BIRTHDAY, BONUS_* reminders (runs daily at 01:00)"""
    from .models import Reminder, ReminderJob
    from apps.patients.models import Patient
    from apps.visits.models import Visit
    
    now = timezone.now()
    today = now.date()
    
    # AFTER_VISIT reminders
    after_visit_reminders = Reminder.objects.filter(
        enabled=True,
        type='AFTER_VISIT'
    )
    
    for reminder in after_visit_reminders:
        # Find visits from N days ago
        target_date = today - timedelta(days=reminder.offset_days)
        
        visits = Visit.objects.filter(
            date=target_date,
            patient__is_marketing_opt_in=True
        ).select_related('patient')
        
        for visit in visits:
            # Check if job already exists
            if not ReminderJob.objects.filter(reminder=reminder, visit=visit).exists():
                scheduled_at = now + timedelta(hours=reminder.offset_hours)
                
                # Adjust for quiet hours
                if is_quiet_hours(scheduled_at):
                    scheduled_at = scheduled_at.replace(hour=8, minute=0, second=0, microsecond=0)
                    if scheduled_at < now:
                        scheduled_at += timedelta(days=1)
                
                ReminderJob.objects.create(
                    reminder=reminder,
                    patient=visit.patient,
                    visit=visit,
                    scheduled_at=scheduled_at,
                    status='queued'
                )
                logger.info(f"Created AFTER_VISIT job for patient {visit.patient.id}")
    
    # BIRTHDAY reminders
    birthday_reminders = Reminder.objects.filter(
        enabled=True,
        type='BIRTHDAY'
    )
    
    for reminder in birthday_reminders:
        # Find patients with birthday today + offset_days
        target_date = today + timedelta(days=reminder.offset_days)
        
        patients = Patient.objects.filter(
            is_marketing_opt_in=True,
            birth_date__month=target_date.month,
            birth_date__day=target_date.day
        )
        
        for patient in patients:
            # Check if job already exists for this year
            if not ReminderJob.objects.filter(
                reminder=reminder,
                patient=patient,
                scheduled_at__year=now.year
            ).exists():
                scheduled_at = now + timedelta(hours=reminder.offset_hours)
                
                # Adjust for quiet hours
                if is_quiet_hours(scheduled_at):
                    scheduled_at = scheduled_at.replace(hour=9, minute=0, second=0, microsecond=0)
                
                ReminderJob.objects.create(
                    reminder=reminder,
                    patient=patient,
                    scheduled_at=scheduled_at,
                    status='queued'
                )
                logger.info(f"Created BIRTHDAY job for patient {patient.id}")
    
    logger.info(f"Reminder job generation completed")


@shared_task
def process_reminder_queue():
    """Process queued reminder jobs (runs every minute)"""
    from .models import ReminderJob, Message, ContactLog
    from .providers import get_sms_provider
    
    now = timezone.now()
    
    # Get jobs ready to send
    jobs = ReminderJob.objects.filter(
        status='queued',
        scheduled_at__lte=now
    ).select_related('reminder', 'patient', 'patient__organization')[:100]  # Batch limit
    
    for job in jobs:
        try:
            # Check if reminder is still enabled
            if not job.reminder.enabled:
                job.status = 'skipped'
                job.error = 'Reminder disabled'
                job.save()
                continue
            
            # Check opt-in
            if not job.patient.is_marketing_opt_in:
                # Allow transactional messages (PREBOOK_*, ONLINE_CONFIRM)
                if job.reminder.type not in ['PREBOOK_CREATE', 'PREBOOK_UPDATE', 'PREBOOK_CANCEL', 'ONLINE_CONFIRM']:
                    job.status = 'skipped'
                    job.error = 'Patient opted out'
                    job.save()
                    continue
            
            # Apply placeholders
            body = apply_placeholders(
                job.reminder.body,
                job.patient,
                visit=job.visit,
                appointment=job.appointment
            )
            
            # Check antispam
            body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
            if check_antispam(job.patient, body_hash, window_hours=24):
                job.status = 'skipped'
                job.error = 'Antispam: same message sent recently'
                job.save()
                logger.warning(f"Skipped job {job.id} due to antispam")
                continue
            
            # Send message
            provider = get_sms_provider(job.patient.organization)
            result = provider.send(
                sender=job.patient.organization.name[:20] if hasattr(job.patient.organization, 'name') else 'CLINIC',
                phone=job.patient.phone,
                body=body
            )
            
            # Create message record
            message = Message.objects.create(
                organization=job.patient.organization,
                patient=job.patient,
                channel=job.reminder.channel,
                body=body,
                sender=job.patient.organization.name[:20] if hasattr(job.patient.organization, 'name') else 'CLINIC',
                context={
                    'source': 'reminder',
                    'source_id': str(job.reminder.id),
                    'job_id': str(job.id)
                },
                status='sent' if result.success else 'failed',
                cost=result.cost,
                provider_msg_id=result.message_id if result.success else '',
                error=result.error,
                sent_at=now if result.success else None
            )
            
            # Create contact log
            ContactLog.objects.create(
                organization=job.patient.organization,
                patient=job.patient,
                channel=job.reminder.channel,
                body_hash=body_hash,
                status='sent' if result.success else 'failed',
                related_visit=job.visit,
                message=message
            )
            
            # Update job
            job.status = 'sent' if result.success else 'failed'
            job.provider_msg_id = result.message_id if result.success else ''
            job.error = result.error
            job.attempts += 1
            job.save()
            
            # Update reminder stats
            if result.success:
                job.reminder.sent_count += 1
                job.reminder.save(update_fields=['sent_count'])
            
            logger.info(f"Processed job {job.id}: {'success' if result.success else 'failed'}")
            
        except Exception as e:
            logger.error(f"Error processing job {job.id}: {e}")
            job.attempts += 1
            if job.attempts >= 5:
                job.status = 'failed'
                job.error = f"Max attempts reached: {str(e)}"
            job.save()


@shared_task
def fetch_delivery_statuses():
    """Fetch delivery statuses from provider (runs every 5 minutes)"""
    from .models import Message, ReminderJob, ContactLog
    from .providers import get_sms_provider
    
    # Get messages sent in last 24 hours but not yet delivered
    cutoff = timezone.now() - timedelta(hours=24)
    messages = Message.objects.filter(
        status='sent',
        sent_at__gte=cutoff,
        provider_msg_id__isnull=False
    ).exclude(provider_msg_id='')[:200]  # Batch limit
    
    for message in messages:
        try:
            provider = get_sms_provider(message.organization)
            status = provider.get_status(message.provider_msg_id)
            
            if status.status == 'delivered':
                message.status = 'delivered'
                message.delivered_at = timezone.now()
                message.save(update_fields=['status', 'delivered_at'])
                
                # Update reminder job if exists
                ReminderJob.objects.filter(provider_msg_id=message.provider_msg_id).update(
                    status='delivered'
                )
                
                # Update contact log
                ContactLog.objects.filter(message=message).update(status='delivered')
                
                # Update reminder stats
                if message.context.get('source') == 'reminder':
                    from .models import Reminder
                    Reminder.objects.filter(id=message.context.get('source_id')).update(
                        delivered_count=F('delivered_count') + 1
                    )
                
                logger.info(f"Message {message.id} delivered")
            
            elif status.status == 'failed':
                message.status = 'failed'
                message.error = status.error
                message.save(update_fields=['status', 'error'])
                
                # Update reminder job if exists
                ReminderJob.objects.filter(provider_msg_id=message.provider_msg_id).update(
                    status='failed',
                    error=status.error
                )
                
                logger.warning(f"Message {message.id} failed: {status.error}")
        
        except Exception as e:
            logger.error(f"Error fetching status for message {message.id}: {e}")


# ==================== Legacy Tasks ====================


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
        result = provider.send(sender='CLINIC', phone=appointment.patient.phone, body=text)
        
        # Log
        MessageLog.objects.create(
            patient=appointment.patient,
            appointment=appointment,
            channel='sms',
            template_key=template.key,
            text=text,
            cost=result.cost,
            status='sent' if result.success else 'failed'
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


@shared_task
def calculate_conversions():
    """
    Calculate conversions by linking visits to messages (runs daily at 02:00)
    Links visits that occurred within 14 days after message was sent
    """
    from .models import Message, ContactLog, Reminder, Campaign
    from apps.visits.models import Visit
    
    # Conversion window: 14 days
    conversion_window_days = 14
    
    # Get messages from last 30 days that need conversion calculation
    cutoff_date = timezone.now() - timedelta(days=30)
    messages = Message.objects.filter(
        status='delivered',
        delivered_at__gte=cutoff_date
    ).select_related('patient', 'organization')
    
    updated_logs = 0
    updated_reminders = {}
    updated_campaigns = {}
    
    for message in messages:
        # Skip if already linked to visit
        contact_log = ContactLog.objects.filter(message=message).first()
        if contact_log and contact_log.related_visit:
            continue
        
        # Find visits by this patient within conversion window
        visit_from = message.delivered_at
        visit_to = visit_from + timedelta(days=conversion_window_days)
        
        visits = Visit.objects.filter(
            patient=message.patient,
            date__gte=visit_from.date(),
            date__lte=visit_to.date()
        ).order_by('date')
        
        if visits.exists():
            # Link to the first visit after message
            visit = visits.first()
            
            # Update or create contact log
            if contact_log:
                contact_log.related_visit = visit
                contact_log.amount = visit.total_amount if hasattr(visit, 'total_amount') else 0
                contact_log.save()
                updated_logs += 1
            else:
                body_hash = hashlib.sha256(message.body.encode('utf-8')).hexdigest()
                ContactLog.objects.create(
                    organization=message.organization,
                    patient=message.patient,
                    channel=message.channel,
                    body_hash=body_hash,
                    status='delivered',
                    related_visit=visit,
                    amount=visit.total_amount if hasattr(visit, 'total_amount') else 0,
                    message=message
                )
                updated_logs += 1
            
            # Update reminder/campaign stats
            source = message.context.get('source')
            source_id = message.context.get('source_id')
            
            if source == 'reminder' and source_id:
                if source_id not in updated_reminders:
                    updated_reminders[source_id] = {
                        'visit_count': 0,
                        'visit_amount': 0
                    }
                updated_reminders[source_id]['visit_count'] += 1
                updated_reminders[source_id]['visit_amount'] += (
                    visit.total_amount if hasattr(visit, 'total_amount') else 0
                )
            
            elif source == 'campaign' and source_id:
                if source_id not in updated_campaigns:
                    updated_campaigns[source_id] = {
                        'visit_count': 0,
                        'visit_amount': 0
                    }
                updated_campaigns[source_id]['visit_count'] += 1
                updated_campaigns[source_id]['visit_amount'] += (
                    visit.total_amount if hasattr(visit, 'total_amount') else 0
                )
    
    # Update reminder stats in bulk
    for reminder_id, stats in updated_reminders.items():
        Reminder.objects.filter(id=reminder_id).update(
            visit_count=F('visit_count') + stats['visit_count'],
            visit_amount=F('visit_amount') + stats['visit_amount']
        )
    
    # Update campaign stats in bulk
    for campaign_id, stats in updated_campaigns.items():
        Campaign.objects.filter(id=campaign_id).update(
            visit_count=F('visit_count') + stats['visit_count'],
            visit_amount=F('visit_amount') + stats['visit_amount']
        )
    
    logger.info(
        f"Conversion calculation completed: {updated_logs} logs updated, "
        f"{len(updated_reminders)} reminders, {len(updated_campaigns)} campaigns"
    )

