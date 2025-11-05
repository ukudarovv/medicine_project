"""
Telegram Bot Models
"""
import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from apps.patients.models import Patient
from apps.calendar.models import Appointment
from apps.org.models import Organization


class PatientTelegramLink(models.Model):
    """
    Link between Patient and Telegram account
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='telegram_link'
    )
    telegram_user_id = models.BigIntegerField(
        unique=True,
        db_index=True,
        help_text='Telegram user ID'
    )
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        help_text='Telegram username (@username)'
    )
    
    # Language preference
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('kk', 'Қазақ'),
    ]
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='ru',
        help_text='Preferred language'
    )
    
    # Consents
    consents_json = models.JSONField(
        default=dict,
        help_text='Consents: personal_data, medical_intervention, marketing'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_interaction_at = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_telegram_links'
        verbose_name = 'Patient Telegram Link'
        verbose_name_plural = 'Patient Telegram Links'
        indexes = [
            models.Index(fields=['telegram_user_id']),
            models.Index(fields=['patient']),
        ]
    
    def __str__(self):
        return f"{self.patient.full_name} - @{self.telegram_username or self.telegram_user_id}"


class BotBroadcast(models.Model):
    """
    Telegram broadcast/mailing campaign
    """
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('scheduled', 'Запланирована'),
        ('running', 'Выполняется'),
        ('completed', 'Завершена'),
        ('failed', 'Ошибка'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='bot_broadcasts'
    )
    
    title = models.CharField(max_length=200, help_text='Название рассылки')
    
    # Segmentation filters
    segment_filters_json = models.JSONField(
        default=dict,
        help_text='Filters: age_min, age_max, sex, services, tags, osms_status, last_visit_from, last_visit_to'
    )
    
    # Messages (multilingual)
    text_ru = models.TextField(help_text='Текст на русском')
    text_kk = models.TextField(blank=True, help_text='Текст на казахском')
    
    # Scheduling
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_recipients = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='bot_broadcasts_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bot_broadcasts'
        verbose_name = 'Bot Broadcast'
        verbose_name_plural = 'Bot Broadcasts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['scheduled_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class BotDocument(models.Model):
    """
    Documents generated for patients via bot
    """
    DOCUMENT_TYPE_CHOICES = [
        ('direction', 'Направление'),
        ('recipe', 'Рецепт'),
        ('tax', 'Справка для налогового вычета'),
        ('result', 'Результат исследования'),
        ('certificate', 'Справка'),
    ]
    
    LANGUAGE_CHOICES = [
        ('ru', 'Русский'),
        ('kk', 'Қазақ'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='bot_documents'
    )
    
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file_path = models.CharField(max_length=500, help_text='Path to PDF file')
    title = models.CharField(max_length=200)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='ru')
    
    # Security - TTL for links
    expires_at = models.DateTimeField(help_text='Link expiration time')
    is_expired = models.BooleanField(default=False)
    
    # Metadata
    related_visit = models.ForeignKey(
        'visits.Visit',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bot_documents'
        verbose_name = 'Bot Document'
        verbose_name_plural = 'Bot Documents'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'document_type']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.patient.full_name}"


class BotAudit(models.Model):
    """
    Audit log for bot actions
    """
    ACTION_CHOICES = [
        ('register', 'Регистрация'),
        ('book', 'Запись на приём'),
        ('cancel', 'Отмена записи'),
        ('reschedule', 'Перенос записи'),
        ('view_doc', 'Просмотр документа'),
        ('payment', 'Оплата'),
        ('feedback', 'Обратная связь'),
        ('other', 'Другое'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_telegram_link = models.ForeignKey(
        PatientTelegramLink,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    payload_json = models.JSONField(
        default=dict,
        help_text='Action details and metadata'
    )
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bot_audit_logs'
        verbose_name = 'Bot Audit Log'
        verbose_name_plural = 'Bot Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_telegram_link', 'created_at']),
            models.Index(fields=['action']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.patient_telegram_link.patient.full_name}"


class BotFeedback(models.Model):
    """
    NPS feedback collected via bot
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='bot_feedbacks'
    )
    patient_telegram_link = models.ForeignKey(
        PatientTelegramLink,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )
    
    # NPS score (0-10)
    score = models.IntegerField(
        help_text='NPS score 0-10'
    )
    comment = models.TextField(blank=True, help_text='Optional comment')
    
    # Alert flag for low scores
    is_low_score = models.BooleanField(
        default=False,
        help_text='True if score <= 6'
    )
    is_reviewed = models.BooleanField(
        default=False,
        help_text='Admin reviewed the feedback'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bot_feedbacks'
        verbose_name = 'Bot Feedback'
        verbose_name_plural = 'Bot Feedbacks'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['appointment']),
            models.Index(fields=['score']),
            models.Index(fields=['is_low_score', 'is_reviewed']),
        ]
    
    def __str__(self):
        return f"NPS {self.score}/10 - {self.patient_telegram_link.patient.full_name}"
    
    def save(self, *args, **kwargs):
        # Auto-set low score flag
        if self.score <= 6:
            self.is_low_score = True
        super().save(*args, **kwargs)


class SupportTicket(models.Model):
    """
    Support tickets created from bot
    """
    STATUS_CHOICES = [
        ('open', 'Открыт'),
        ('in_progress', 'В работе'),
        ('resolved', 'Решён'),
        ('closed', 'Закрыт'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_telegram_link = models.ForeignKey(
        PatientTelegramLink,
        on_delete=models.CASCADE,
        related_name='support_tickets'
    )
    
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    assigned_to = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'support_tickets'
        verbose_name = 'Support Ticket'
        verbose_name_plural = 'Support Tickets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient_telegram_link', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.subject} - {self.get_status_display()}"

