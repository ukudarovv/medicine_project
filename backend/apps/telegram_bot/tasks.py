"""
Celery tasks for Telegram bot
"""
from celery import shared_task
import requests
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_consent_request(self, telegram_user_id, access_request_id, org_name, reason, scopes, otp_code, language='ru'):
    """
    Send consent request notification to patient via Telegram
    
    Args:
        telegram_user_id: Telegram user ID
        access_request_id: AccessRequest UUID
        org_name: Organization name requesting access
        reason: Reason for access request
        scopes: List of requested scopes
        otp_code: 6-digit OTP code
        language: Language code (ru/kk), default 'ru'
    """
    try:
        from django.conf import settings
        
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not bot_token:
            logger.error('TELEGRAM_BOT_TOKEN not configured')
            return False
        
        # Get patient's language preference
        try:
            from apps.telegram_bot.models import PatientTelegramLink
            tg_link = PatientTelegramLink.objects.get(telegram_user_id=telegram_user_id)
            language = tg_link.language
        except:
            pass  # Use default language
        
        # Translations
        translations = {
            'ru': {
                'title': '🏥 <b>Запрос доступа к вашей медицинской карте</b>',
                'org': '<b>Организация:</b>',
                'reason': '<b>Причина:</b>',
                'requested_access': '<b>Запрашиваемый доступ:</b>',
                'confirmation_code': '<b>Код подтверждения:</b>',
                'validity': '❗️ Код действителен 10 минут.',
                'instruction': 'Используйте кнопку ниже для подтверждения или отклонения запроса.',
                'approve': '✅ Разрешить',
                'deny': '❌ Отклонить',
                'details': 'ℹ️ Подробнее',
                'scopes': {
                    'read_summary': 'Чтение краткой информации',
                    'read_records': 'Чтение медицинских записей',
                    'write_records': 'Создание медицинских записей',
                    'read_images': 'Просмотр изображений и файлов'
                }
            },
            'kk': {
                'title': '🏥 <b>Медициналық картаңызға қол жеткізу сұрауы</b>',
                'org': '<b>Ұйым:</b>',
                'reason': '<b>Себебі:</b>',
                'requested_access': '<b>Сұралған қол жеткізу:</b>',
                'confirmation_code': '<b>Растау коды:</b>',
                'validity': '❗️ Код 10 минут жарамды.',
                'instruction': 'Растау немесе қабылдамау үшін төмендегі батырманы пайдаланыңыз.',
                'approve': '✅ Рұқсат беру',
                'deny': '❌ Қабылдамау',
                'details': 'ℹ️ Толығырақ',
                'scopes': {
                    'read_summary': 'Қысқаша ақпаратты оқу',
                    'read_records': 'Медициналық жазбаларды оқу',
                    'write_records': 'Медициналық жазбаларды жасау',
                    'read_images': 'Суреттер мен файлдарды қарау'
                }
            }
        }
        
        t = translations.get(language, translations['ru'])
        
        # Format scopes for display
        scopes_text = '\n'.join([f'• {t["scopes"].get(s, s)}' for s in scopes])
        
        # Compose message
        message = (
            f"{t['title']}\n\n"
            f"{t['org']} {org_name}\n"
            f"{t['reason']} {reason}\n\n"
            f"{t['requested_access']}\n{scopes_text}\n\n"
            f"{t['confirmation_code']} <code>{otp_code}</code>\n\n"
            f"{t['validity']}\n"
            f"{t['instruction']}"
        )
        
        # Inline keyboard
        keyboard = {
            'inline_keyboard': [
                [
                    {'text': t['approve'], 'callback_data': f'consent_approve:{access_request_id}:{otp_code}'},
                    {'text': t['deny'], 'callback_data': f'consent_deny:{access_request_id}'}
                ],
                [
                    {'text': t['details'], 'callback_data': f'consent_details:{access_request_id}'}
                ]
            ]
        }
        
        # Send message via Telegram Bot API
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        payload = {
            'chat_id': telegram_user_id,
            'text': message,
            'parse_mode': 'HTML',
            'reply_markup': keyboard
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info(f'Consent request sent to Telegram user {telegram_user_id} (lang: {language})')
        return True
        
    except requests.exceptions.RequestException as e:
        # Retry on network errors
        logger.warning(f'Network error sending consent request, retrying: {e}')
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        
    except Exception as e:
        logger.error(f'Failed to send consent request via Telegram: {e}')
        # Don't retry on other errors
        return False


@shared_task
def send_consent_approved_notification(telegram_user_id, org_name, valid_to):
    """
    Send notification that consent was approved
    """
    try:
        from django.conf import settings
        
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not bot_token:
            return False
        
        message = (
            f"✅ <b>Доступ предоставлен</b>\n\n"
            f"Организация <b>{org_name}</b> получила доступ к вашей медицинской карте.\n\n"
            f"<b>Доступ действителен до:</b> {valid_to}\n\n"
            f"Вы можете отозвать доступ в любой момент через раздел 'Мои доступы'."
        )
        
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        payload = {
            'chat_id': telegram_user_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        return True
        
    except Exception as e:
        logger.error(f'Failed to send consent approved notification: {e}')
        return False


@shared_task
def send_consent_denied_notification(telegram_user_id, org_name):
    """
    Send notification that consent was denied
    """
    try:
        from django.conf import settings
        
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not bot_token:
            return False
        
        message = (
            f"❌ <b>Доступ отклонён</b>\n\n"
            f"Вы отклонили запрос доступа от организации <b>{org_name}</b>."
        )
        
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        payload = {
            'chat_id': telegram_user_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        return True
        
    except Exception as e:
        logger.error(f'Failed to send consent denied notification: {e}')
        return False


@shared_task
def create_audit_log_async(user_id, organization_id, patient_id, action, object_type, object_id, grant_id, ip_address, user_agent, details):
    """
    Create audit log entry asynchronously
    Used by AuditLoggingMiddleware
    """
    try:
        from apps.consent.models import AuditLog, AccessGrant
        from apps.core.models import User
        from apps.org.models import Organization
        from apps.patients.models import Patient
        
        # Get objects
        user = User.objects.get(id=user_id) if user_id else None
        organization = Organization.objects.get(id=organization_id) if organization_id else None
        patient = Patient.objects.get(id=patient_id) if patient_id else None
        grant = AccessGrant.objects.get(id=grant_id) if grant_id else None
        
        # Create audit log
        AuditLog.objects.create(
            user=user,
            organization=organization,
            patient=patient,
            action=action,
            object_type=object_type,
            object_id=str(object_id) if object_id else '',
            access_grant=grant,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
        
        logger.info(f'Audit log created for {action} on {object_type} by user {user_id}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to create audit log: {e}')
        return False


@shared_task(bind=True, max_retries=3)
def process_broadcast(self, broadcast_id):
    """
    Process and send broadcast messages to recipients
    
    Args:
        broadcast_id: UUID of the BotBroadcast
    """
    try:
        from django.conf import settings
        from apps.telegram_bot.models import BotBroadcast, PatientTelegramLink
        
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        if not bot_token:
            logger.error('TELEGRAM_BOT_TOKEN not configured')
            return False
        
        # Get broadcast
        broadcast = BotBroadcast.objects.get(id=broadcast_id)
        
        # Update status
        broadcast.status = 'in_progress'
        broadcast.save()
        
        # Get recipients based on segment
        recipients = PatientTelegramLink.objects.filter(is_active=True)
        
        if broadcast.segment_filter:
            # Apply segment filters if any
            segment_filter = broadcast.segment_filter
            if 'language' in segment_filter:
                recipients = recipients.filter(language=segment_filter['language'])
            if 'organization_id' in segment_filter:
                recipients = recipients.filter(patient__organizations__id=segment_filter['organization_id'])
        
        broadcast.total_recipients = recipients.count()
        broadcast.save()
        
        # Send messages
        url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
        sent_count = 0
        failed_count = 0
        
        for recipient in recipients:
            try:
                payload = {
                    'chat_id': recipient.telegram_user_id,
                    'text': broadcast.message,
                    'parse_mode': 'HTML'
                }
                
                # Add inline keyboard if buttons exist
                if broadcast.buttons:
                    keyboard = {'inline_keyboard': []}
                    for button in broadcast.buttons:
                        keyboard['inline_keyboard'].append([{
                            'text': button.get('text', ''),
                            'url': button.get('url', '')
                        }])
                    payload['reply_markup'] = keyboard
                
                response = requests.post(url, json=payload, timeout=10)
                response.raise_for_status()
                
                sent_count += 1
                logger.info(f'Broadcast message sent to {recipient.telegram_user_id}')
                
            except Exception as e:
                failed_count += 1
                logger.error(f'Failed to send broadcast to {recipient.telegram_user_id}: {e}')
            
            # Update progress
            broadcast.sent_count = sent_count
            broadcast.failed_count = failed_count
            broadcast.save()
        
        # Mark as completed
        broadcast.status = 'completed'
        broadcast.save()
        
        logger.info(f'Broadcast {broadcast_id} completed: {sent_count} sent, {failed_count} failed')
        return True
        
    except Exception as e:
        logger.error(f'Failed to process broadcast {broadcast_id}: {e}')
        # Retry on errors
        raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))