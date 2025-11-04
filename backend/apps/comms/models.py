import uuid
import hashlib
from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.patients.models import Patient
from apps.calendar.models import Appointment


class Template(models.Model):
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
    ]
    
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    key = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=500, blank=True)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'templates'
    
    def __str__(self):
        return f"{self.key} ({self.channel})"


class MessageLog(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.SET_NULL, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    channel = models.CharField(max_length=20)
    template_key = models.CharField(max_length=100, blank=True)
    text = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_logs'
        ordering = ['-created_at']


# ==================== Marketing Models ====================


class SmsProvider(models.Model):
    """SMS Provider configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('org.Organization', on_delete=models.CASCADE, related_name='sms_providers')
    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=500, help_text='API key (will be encrypted)')
    api_secret = models.CharField(max_length=500, blank=True, help_text='API secret (will be encrypted)')
    sender_name = models.CharField(max_length=20, help_text='Default sender name')
    rate_limit_per_min = models.IntegerField(default=30, help_text='Rate limit per minute')
    price_per_sms = models.DecimalField(max_digits=10, decimal_places=2, default=15.0, help_text='Price per SMS in KZT')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sms_providers'
        verbose_name = 'SMS Provider'
        verbose_name_plural = 'SMS Providers'
    
    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class Campaign(models.Model):
    """Marketing campaign (bulk SMS)"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('paused', 'Paused'),
        ('finished', 'Finished'),
        ('failed', 'Failed'),
    ]
    
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('org.Organization', on_delete=models.CASCADE, related_name='campaigns')
    title = models.CharField(max_length=200)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='sms')
    sender_name = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    visit_count = models.IntegerField(default=0, help_text='Визитов после рассылки')
    visit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text='Сумма визитов')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, related_name='campaigns_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'campaigns'
        ordering = ['-created_at']
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaigns'
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    @property
    def delivered_rate(self):
        """Delivery rate"""
        if self.sent_count == 0:
            return 0
        return round((self.delivered_count / self.sent_count) * 100, 2)
    
    @property
    def conversion_rate(self):
        """Conversion rate (visits / delivered)"""
        if self.delivered_count == 0:
            return 0
        return round((self.visit_count / self.delivered_count) * 100, 2)


class CampaignAudience(models.Model):
    """Campaign audience filters"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name='audience')
    filters = models.JSONField(default=dict, help_text='Audience filters: tags, services, last_visit, birthdate, opt_in')
    
    class Meta:
        db_table = 'campaign_audiences'
    
    def __str__(self):
        return f"Audience for {self.campaign.title}"


class CampaignMessageTemplate(models.Model):
    """Campaign message template"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name='message_template')
    body = models.TextField(help_text='Message body with placeholders')
    placeholders = models.JSONField(default=list, help_text='Available placeholders')
    max_segments = models.IntegerField(default=1, help_text='Maximum SMS segments')
    
    class Meta:
        db_table = 'campaign_message_templates'
    
    def __str__(self):
        return f"Template for {self.campaign.title}"


class CampaignRecipient(models.Model):
    """Campaign recipient (materialized list)"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('opted_out', 'Opted Out'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='recipients')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='campaign_recipients')
    phone = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    provider_msg_id = models.CharField(max_length=200, blank=True)
    error = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'campaign_recipients'
        ordering = ['campaign', 'created_at']
        indexes = [
            models.Index(fields=['campaign', 'status']),
            models.Index(fields=['patient']),
        ]
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.get_status_display()}"


class Reminder(models.Model):
    """Reminder (trigger scenario)"""
    TYPE_CHOICES = [
        ('MISSED_CALL', 'Пропущенный звонок'),
        ('PREBOOK_CREATE', 'Создание предварительной записи'),
        ('PREBOOK_UPDATE', 'Изменение предварительной записи'),
        ('PREBOOK_DELETE', 'Удаление предварительной записи'),
        ('PREBOOK_CANCEL', 'Отмена предварительной записи'),
        ('ONLINE_CONFIRM', 'Подтверждение онлайн-записи'),
        ('AFTER_VISIT', 'После визита'),
        ('BIRTHDAY', 'День рождения'),
        ('BONUS_LEFT', 'Остаток бонусов'),
        ('BONUS_WRITEOFF', 'Списание бонусов'),
        ('CUSTOM', 'Произвольное'),
    ]
    
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('call', 'Звонок-робот'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('org.Organization', on_delete=models.CASCADE, related_name='reminders')
    name = models.CharField(max_length=200)
    enabled = models.BooleanField(default=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    link_service = models.ForeignKey('services.Service', on_delete=models.SET_NULL, null=True, blank=True, help_text='Связанная услуга (опционально)')
    
    # Timing
    offset_days = models.IntegerField(default=0, help_text='Дней после события')
    offset_hours = models.IntegerField(default=0, help_text='Часов после события')
    
    # Channel and content
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='sms')
    body = models.TextField(help_text='Message body with placeholders')
    
    # Statistics
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    visit_count = models.IntegerField(default=0)
    online_bookings_count = models.IntegerField(default=0)
    visit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, related_name='reminders_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reminders'
        ordering = ['-created_at']
        verbose_name = 'Reminder'
        verbose_name_plural = 'Reminders'
        indexes = [
            models.Index(fields=['organization', 'enabled']),
            models.Index(fields=['type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    @property
    def conversion_rate(self):
        """Conversion rate"""
        if self.delivered_count == 0:
            return 0
        return round((self.visit_count / self.delivered_count) * 100, 2)


class ReminderJob(models.Model):
    """Reminder job queue"""
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, related_name='jobs')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reminder_jobs')
    visit = models.ForeignKey('visits.Visit', on_delete=models.SET_NULL, null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.SET_NULL, null=True, blank=True)
    
    scheduled_at = models.DateTimeField(help_text='Scheduled send time')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    provider_msg_id = models.CharField(max_length=200, blank=True)
    error = models.TextField(blank=True)
    attempts = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reminder_jobs'
        ordering = ['scheduled_at']
        indexes = [
            models.Index(fields=['reminder', 'status']),
            models.Index(fields=['scheduled_at', 'status']),
            models.Index(fields=['patient']),
        ]
    
    def __str__(self):
        return f"{self.reminder.name} -> {self.patient.full_name} ({self.get_status_display()})"


class Message(models.Model):
    """Message (unit of sending)"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('email', 'Email'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('org.Organization', on_delete=models.CASCADE, related_name='messages')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='messages')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    body = models.TextField()
    sender = models.CharField(max_length=50)
    
    # Context (source of message)
    context = models.JSONField(default=dict, help_text='Source: campaign/reminder/manual + source_id')
    
    # Status and delivery
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    provider_msg_id = models.CharField(max_length=200, blank=True)
    error = models.TextField(blank=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['patient']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.channel} to {self.patient.full_name} ({self.get_status_display()})"


class SmsBalanceSnapshot(models.Model):
    """SMS balance snapshot (for reporting)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('org.Organization', on_delete=models.CASCADE, related_name='sms_balance_snapshots')
    provider = models.ForeignKey(SmsProvider, on_delete=models.SET_NULL, null=True, blank=True)
    
    period_from = models.DateField()
    period_to = models.DateField()
    
    sent = models.IntegerField(default=0)
    delivered = models.IntegerField(default=0)
    failed = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sms_balance_snapshots'
        ordering = ['-period_from']
        indexes = [
            models.Index(fields=['organization', 'period_from', 'period_to']),
        ]
    
    def __str__(self):
        return f"{self.organization.name}: {self.period_from} - {self.period_to}"


class ContactLog(models.Model):
    """Contact log (for reporting)"""
    CHANNEL_CHOICES = [
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('email', 'Email'),
        ('call', 'Call'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('org.Organization', on_delete=models.CASCADE, related_name='contact_logs')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='contact_logs')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    body_hash = models.CharField(max_length=64, help_text='SHA256 hash of message body')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    related_visit = models.ForeignKey('visits.Visit', on_delete=models.SET_NULL, null=True, blank=True, help_text='Связанный визит (для конверсии)')
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text='Сумма визита')
    
    # Link to original message
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'contact_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['patient', 'created_at']),
            models.Index(fields=['channel']),
        ]
    
    def __str__(self):
        return f"{self.channel} to {self.patient.full_name} at {self.created_at}"
    
    @staticmethod
    def hash_body(body: str) -> str:
        """Generate SHA256 hash of message body"""
        return hashlib.sha256(body.encode('utf-8')).hexdigest()


class PatientContact(models.Model):
    """
    Patient contact history (calls, visits, SMS) - Sprint 2
    Detailed contact tracking for patient management
    """
    CONTACT_TYPE_CHOICES = [
        ('call', 'Звонок'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('visit', 'Визит в клинику'),
        ('email', 'Email'),
    ]
    
    DIRECTION_CHOICES = [
        ('inbound', 'Входящий'),
        ('outbound', 'Исходящий'),
    ]
    
    STATUS_CHOICES = [
        ('reached', 'Дозвонились'),
        ('no_answer', 'Не ответил'),
        ('callback_requested', 'Перезвонить'),
        ('message_left', 'Оставлено сообщение'),
        ('completed', 'Выполнено'),
    ]
    
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='contact_interactions'
    )
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    
    note = models.TextField(blank=True, help_text='Заметка о контакте')
    next_contact_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Дата следующего контакта'
    )
    
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='patient_contacts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'patient_contacts'
        verbose_name = 'Patient Contact'
        verbose_name_plural = 'Patient Contacts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'created_at']),
            models.Index(fields=['contact_type', 'status']),
            models.Index(fields=['next_contact_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - {self.get_contact_type_display()} ({self.created_at.date()})"


class AuditLog(models.Model):
    """Audit log for marketing actions"""
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('send', 'Send'),
        ('pause', 'Pause'),
        ('resume', 'Resume'),
    ]
    
    ENTITY_CHOICES = [
        ('campaign', 'Campaign'),
        ('reminder', 'Reminder'),
        ('message', 'Message'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey('org.Organization', on_delete=models.CASCADE, related_name='marketing_audit_logs')
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True)
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    entity_id = models.UUIDField()
    
    changes = models.JSONField(default=dict, help_text='Changes made')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'marketing_audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user} {self.action} {self.entity_type} at {self.created_at}"

