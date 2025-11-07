"""
Consent system models for multi-org patient access

Models:
- AccessRequest: Request to access patient data from another organization
- ConsentToken: OTP token for verifying consent
- AccessGrant: Granted access to patient data
- AuditLog: Immutable audit trail of all access events
"""
import uuid
import secrets
from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from apps.patients.models import Patient
from apps.org.models import Organization
from apps.core.models import User


class AccessRequest(models.Model):
    """
    Request for access to patient data from another organization
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает ответа'),
        ('approved', 'Одобрено'),
        ('denied', 'Отклонено'),
        ('expired', 'Истекло'),
    ]
    
    DELIVERY_CHANNEL_CHOICES = [
        ('telegram', 'Telegram'),
        ('sms', 'SMS'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who and what
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='access_requests'
    )
    requester_org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='access_requests_made',
        help_text='Organization requesting access'
    )
    requester_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='access_requests_made',
        help_text='User who requested access'
    )
    
    # Access scopes
    SCOPE_CHOICES = [
        ('read_summary', 'Чтение краткой информации'),
        ('read_records', 'Чтение медицинских записей'),
        ('write_records', 'Создание медицинских записей'),
        ('read_images', 'Просмотр изображений и файлов'),
    ]
    scopes = ArrayField(
        models.CharField(max_length=50),
        default=list,
        help_text='Requested access scopes (read_summary, read_records, write_records, read_images)'
    )
    
    # Request details
    reason = models.TextField(help_text='Reason for requesting access')
    requested_duration_days = models.IntegerField(
        default=30,
        help_text='Requested access duration in days'
    )
    
    # Status and delivery
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    delivery_channel = models.CharField(
        max_length=20,
        choices=DELIVERY_CHANNEL_CHOICES,
        default='telegram'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_at = models.DateTimeField(
        help_text='Request expiration time (TTL)'
    )
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'consent_access_requests'
        verbose_name = 'Access Request'
        verbose_name_plural = 'Access Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'status']),
            models.Index(fields=['requester_org', 'created_at']),
            models.Index(fields=['status', 'expires_at']),
        ]
    
    def __str__(self):
        return f"{self.requester_org.name} → {self.patient.full_name} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Set expiration time if not set
        if not self.expires_at:
            from django.conf import settings
            ttl_minutes = getattr(settings, 'CONSENT_OTP_TTL_MINUTES', 10)
            self.expires_at = timezone.now() + timedelta(minutes=ttl_minutes)
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if request has expired"""
        return timezone.now() > self.expires_at and self.status == 'pending'
    
    def mark_expired(self):
        """Mark request as expired"""
        if self.status == 'pending':
            self.status = 'expired'
            self.responded_at = timezone.now()
            self.save(update_fields=['status', 'responded_at'])


class ConsentToken(models.Model):
    """
    OTP token for verifying consent
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    access_request = models.OneToOneField(
        AccessRequest,
        on_delete=models.CASCADE,
        related_name='consent_token'
    )
    
    # OTP code (hashed with bcrypt)
    otp_code_hash = models.CharField(max_length=128, help_text='Bcrypt hash of OTP code')
    
    # Metadata
    attempts_count = models.IntegerField(default=0, help_text='Number of verification attempts')
    max_attempts = models.IntegerField(default=3, help_text='Maximum allowed attempts')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text='Token expiration time')
    used_at = models.DateTimeField(null=True, blank=True, help_text='Time when token was successfully used')
    
    class Meta:
        db_table = 'consent_tokens'
        verbose_name = 'Consent Token'
        verbose_name_plural = 'Consent Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.access_request}"
    
    @staticmethod
    def generate_otp_code():
        """Generate a 6-digit OTP code"""
        return f"{secrets.randbelow(1000000):06d}"
    
    @staticmethod
    def hash_otp(otp_code: str) -> str:
        """Hash OTP code with bcrypt"""
        import bcrypt
        return bcrypt.hashpw(otp_code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_otp(self, otp_code: str) -> bool:
        """
        Verify OTP code
        
        Returns:
            True if code is valid, False otherwise
        """
        import bcrypt
        
        # Check if expired
        if timezone.now() > self.expires_at:
            return False
        
        # Check if already used
        if self.used_at:
            return False
        
        # Check attempts
        if self.attempts_count >= self.max_attempts:
            return False
        
        # Increment attempts
        self.attempts_count += 1
        self.save(update_fields=['attempts_count'])
        
        # Verify hash
        try:
            is_valid = bcrypt.checkpw(
                otp_code.encode('utf-8'),
                self.otp_code_hash.encode('utf-8')
            )
            
            if is_valid:
                self.used_at = timezone.now()
                self.save(update_fields=['used_at'])
            
            return is_valid
        except Exception:
            return False


class AccessGrant(models.Model):
    """
    Granted access to patient data
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who and what
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='access_grants'
    )
    grantee_org = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='access_grants_received',
        help_text='Organization that receives access'
    )
    
    # Related request
    access_request = models.OneToOneField(
        AccessRequest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='grant'
    )
    
    # Access scopes
    scopes = ArrayField(
        models.CharField(max_length=50),
        default=list,
        help_text='Granted access scopes'
    )
    
    # Validity period
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(help_text='Grant expiration time')
    
    # Metadata
    created_by = models.CharField(
        max_length=20,
        default='patient',
        help_text='Who created this grant (patient, system, admin)'
    )
    is_whitelist = models.BooleanField(
        default=False,
        help_text='Long-term trusted access (whitelist)'
    )
    
    # Revocation
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Time when grant was revoked'
    )
    revoked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='revoked_grants'
    )
    revocation_reason = models.TextField(blank=True)
    
    # Access tracking
    last_accessed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time this grant was used'
    )
    access_count = models.IntegerField(
        default=0,
        help_text='Number of times this grant was used'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consent_access_grants'
        verbose_name = 'Access Grant'
        verbose_name_plural = 'Access Grants'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'grantee_org']),
            models.Index(fields=['grantee_org', 'valid_to']),
            models.Index(fields=['valid_to', 'revoked_at']),
        ]
    
    def __str__(self):
        return f"{self.grantee_org.name} → {self.patient.full_name} (до {self.valid_to.date()})"
    
    def is_active(self):
        """Check if grant is currently active"""
        now = timezone.now()
        return (
            self.valid_from <= now <= self.valid_to and
            self.revoked_at is None
        )
    
    def has_scope(self, scope: str) -> bool:
        """Check if grant includes a specific scope"""
        return scope in self.scopes
    
    def revoke(self, user=None, reason=''):
        """Revoke this grant"""
        self.revoked_at = timezone.now()
        self.revoked_by = user
        self.revocation_reason = reason
        self.save(update_fields=['revoked_at', 'revoked_by', 'revocation_reason'])
    
    def track_access(self):
        """Track that this grant was used"""
        self.last_accessed_at = timezone.now()
        self.access_count += 1
        self.save(update_fields=['last_accessed_at', 'access_count'])


class AuditLog(models.Model):
    """
    Immutable audit trail of all access events
    """
    ACTION_CHOICES = [
        ('read', 'Чтение'),
        ('write', 'Запись'),
        ('share', 'Предоставление доступа'),
        ('revoke', 'Отзыв доступа'),
        ('request', 'Запрос доступа'),
        ('deny', 'Отказ в доступе'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    
    # What
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    # Object reference (polymorphic)
    object_type = models.CharField(
        max_length=50,
        blank=True,
        help_text='Type of object accessed (Visit, PatientFile, etc.)'
    )
    object_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID of object accessed'
    )
    
    # Access grant used
    access_grant = models.ForeignKey(
        AccessGrant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Request metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Additional context
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional context and metadata'
    )
    
    # When
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'consent_audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['organization', 'action', 'created_at']),
        ]
        # Make audit logs immutable
        permissions = [
            ('view_audit_log', 'Can view audit logs'),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.patient.full_name} by {self.user} at {self.created_at}"
    
    def save(self, *args, **kwargs):
        # Prevent updates to existing audit logs
        # Check if this is an update (not a new record)
        if self.pk and not kwargs.get('force_insert', False):
            # If pk exists and we're in the database, prevent update
            if self.__class__.objects.filter(pk=self.pk).exists():
                raise Exception('Audit logs are immutable and cannot be modified')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Prevent deletion of audit logs
        raise Exception('Audit logs are immutable and cannot be deleted')

