"""
Serializers for consent system API
"""
from rest_framework import serializers
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import AccessRequest, ConsentToken, AccessGrant, AuditLog
from apps.patients.models import Patient
from apps.patients.utils.encryption import hash_iin, mask_iin


class PatientSearchSerializer(serializers.Serializer):
    """
    Serializer for searching patients by IIN
    """
    iin = serializers.CharField(required=True, max_length=12)
    
    def validate_iin(self, value):
        # Remove whitespace and dashes
        iin = value.replace(' ', '').replace('-', '')
        
        # Basic validation
        if not iin.isdigit():
            raise serializers.ValidationError('ИИН должен содержать только цифры')
        
        if len(iin) != 12:
            raise serializers.ValidationError('ИИН должен состоять из 12 цифр')
        
        return iin


class PatientSearchResultSerializer(serializers.Serializer):
    """
    Minimal patient data for search results
    """
    id = serializers.IntegerField()
    fio_masked = serializers.SerializerMethodField()
    age = serializers.IntegerField()
    has_telegram = serializers.SerializerMethodField()
    iin_masked = serializers.SerializerMethodField()
    
    def get_fio_masked(self, obj):
        """Return partially masked full name"""
        # Show full last name, mask first/middle names
        first = obj.first_name[0] + '*' * (len(obj.first_name) - 1) if obj.first_name else ''
        middle = obj.middle_name[0] + '.' if obj.middle_name else ''
        return f"{obj.last_name} {first} {middle}"
    
    def get_has_telegram(self, obj):
        """Check if patient has Telegram linked"""
        # Check if patient has any Telegram social network
        try:
            return obj.social_networks.filter(network='telegram').exists()
        except Exception:
            return False
    
    def get_iin_masked(self, obj):
        """Return masked IIN"""
        iin = obj.iin_decrypted
        return mask_iin(iin) if iin else ''


class AccessRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for creating access requests
    """
    patient_iin = serializers.CharField(write_only=True, required=True)
    requester_org_name = serializers.CharField(source='requester_org.name', read_only=True)
    requester_user_name = serializers.SerializerMethodField(read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    grant_id = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = AccessRequest
        fields = [
            'id', 'patient', 'patient_iin', 'patient_name',
            'requester_org', 'requester_org_name',
            'requester_user', 'requester_user_name',
            'scopes', 'reason', 'requested_duration_days',
            'status', 'status_display', 'delivery_channel',
            'created_at', 'expires_at', 'responded_at', 'grant_id'
        ]
        read_only_fields = ['id', 'patient', 'requester_org', 'requester_user', 
                           'status', 'created_at', 'expires_at', 'responded_at', 'grant_id']
    
    def get_requester_user_name(self, obj):
        if obj.requester_user:
            return obj.requester_user.get_full_name() or obj.requester_user.username
        return None
    
    def get_grant_id(self, obj):
        """Return grant ID if access request was approved"""
        if hasattr(obj, 'grant') and obj.grant:
            return str(obj.grant.id)
        return None
    
    def validate_patient_iin(self, value):
        # Remove whitespace and dashes
        iin = value.replace(' ', '').replace('-', '')
        
        # Find patient by IIN hash
        iin_hash_value = hash_iin(iin)
        try:
            patient = Patient.objects.get(iin_hash=iin_hash_value)
            return patient.id
        except Patient.DoesNotExist:
            raise serializers.ValidationError('Пациент с таким ИИН не найден')
    
    def validate_scopes(self, value):
        # Validate scopes
        valid_scopes = ['read_summary', 'read_records', 'write_records', 'read_images']
        for scope in value:
            if scope not in valid_scopes:
                raise serializers.ValidationError(f'Неверный scope: {scope}')
        
        if not value:
            raise serializers.ValidationError('Необходимо указать хотя бы один scope')
        
        return value
    
    def validate(self, attrs):
        # Check rate limiting
        patient_id = attrs.get('patient_iin')  # Actually patient ID after validation
        
        if patient_id and hasattr(self.context.get('request'), 'user'):
            user = self.context['request'].user
            org = user.organization
            
            # Check rate limiting with Redis
            from apps.consent.rate_limiting import ConsentRateLimiter, ConsentFraudDetector
            
            rate_check = ConsentRateLimiter.check_rate_limit(org.id, patient_id)
            if not rate_check['allowed']:
                raise serializers.ValidationError(
                    f"Превышен лимит запросов ({rate_check['limit']} в день) для этого пациента. "
                    f"Повторите попытку через {rate_check['reset_in'] // 60} минут."
                )
            
            # Check for denial lockout
            lockout_check = ConsentRateLimiter.check_denial_lockout(org.id, patient_id)
            if lockout_check['locked_out']:
                raise serializers.ValidationError(
                    f"Запросы к этому пациенту временно заблокированы из-за многократных отказов. "
                    f"Повторите попытку через {lockout_check['reset_in'] // 60} минут."
                )
            
            # Fraud detection
            fraud_check = ConsentFraudDetector.check_suspicious_activity(
                user, org, patient_id, 'request'
            )
            
            if fraud_check['suspicious'] and fraud_check['severity'] == 'high':
                # Log suspicious activity
                ConsentFraudDetector.log_suspicious_activity(
                    user, org, patient_id, fraud_check
                )
                
                # Block high-severity suspicious activity
                raise serializers.ValidationError(
                    'Обнаружена подозрительная активность. Запрос заблокирован.'
                )
        
        return attrs
    
    def create(self, validated_data):
        # Extract patient ID from patient_iin field
        patient_id = validated_data.pop('patient_iin')
        patient = Patient.objects.get(id=patient_id)
        
        # Get user and org from context
        user = self.context['request'].user
        org = user.organization
        
        # Increment rate limiter
        from apps.consent.rate_limiting import ConsentRateLimiter
        ConsentRateLimiter.increment(org.id, patient.id)
        
        # Create access request
        access_request = AccessRequest.objects.create(
            patient=patient,
            requester_org=org,
            requester_user=user,
            **validated_data
        )
        
        # Create OTP token (simplified mode: always 1234)
        otp_code = "1234"  # Simplified for testing
        otp_hash = ConsentToken.hash_otp(otp_code)
        
        ttl_minutes = getattr(settings, 'CONSENT_OTP_TTL_MINUTES', 10)
        token = ConsentToken.objects.create(
            access_request=access_request,
            otp_code_hash=otp_hash,
            expires_at=timezone.now() + timedelta(minutes=ttl_minutes)
        )
        
        # Auto-approve for testing (no Telegram needed)
        access_request.status = 'approved'
        access_request.responded_at = timezone.now()
        access_request.save()
        
        # Create grant immediately
        grant_days = getattr(settings, 'CONSENT_GRANT_DEFAULT_DAYS', 30)
        grant = AccessGrant.objects.create(
            patient=patient,
            grantee_org=org,
            access_request=access_request,
            scopes=access_request.scopes,
            valid_to=timezone.now() + timedelta(days=grant_days),
            created_by='system'
        )
        
        # Log both request and grant creation
        AuditLog.objects.create(
            user=user,
            organization=org,
            patient=patient,
            action='share',
            access_grant=grant,
            details={
                'access_request_id': str(access_request.id),
                'grant_id': str(grant.id),
                'scopes': grant.scopes,
                'reason': access_request.reason,
                'auto_approved': True
            }
        )
        
        return access_request
    
    def _send_otp_notification(self, access_request, otp_code):
        """
        Send OTP notification to patient via Telegram
        """
        try:
            # Check if patient has Telegram linked
            if not hasattr(access_request.patient, 'telegram_link'):
                return
            
            telegram_link = access_request.patient.telegram_link
            if not telegram_link:
                return
            
            # Import here to avoid circular dependency
            from apps.telegram_bot.tasks import send_consent_request
            
            # Send notification via Celery task
            send_consent_request.delay(
                telegram_user_id=telegram_link.telegram_user_id,
                access_request_id=str(access_request.id),
                org_name=access_request.requester_org.name,
                reason=access_request.reason,
                scopes=access_request.scopes,
                otp_code=otp_code
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'Failed to send OTP notification: {e}')


class OTPVerifySerializer(serializers.Serializer):
    """
    Serializer for OTP verification
    """
    access_request_id = serializers.UUIDField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6)
    
    def validate_otp_code(self, value):
        if not value.isdigit() or len(value) != 6:
            raise serializers.ValidationError('OTP должен состоять из 6 цифр')
        return value
    
    def validate(self, attrs):
        access_request_id = attrs['access_request_id']
        otp_code = attrs['otp_code']
        
        # Get access request
        try:
            access_request = AccessRequest.objects.get(id=access_request_id)
        except AccessRequest.DoesNotExist:
            raise serializers.ValidationError('Запрос доступа не найден')
        
        # Check if already processed
        if access_request.status != 'pending':
            raise serializers.ValidationError(f'Запрос уже обработан: {access_request.get_status_display()}')
        
        # Check if expired
        if access_request.is_expired():
            access_request.mark_expired()
            raise serializers.ValidationError('Запрос истёк')
        
        # Get token
        try:
            token = access_request.consent_token
        except ConsentToken.DoesNotExist:
            raise serializers.ValidationError('Токен не найден')
        
        # Verify OTP
        if not token.verify_otp(otp_code):
            raise serializers.ValidationError('Неверный OTP код')
        
        attrs['access_request'] = access_request
        return attrs
    
    def create_grant(self):
        """
        Create access grant after successful OTP verification
        """
        access_request = self.validated_data['access_request']
        
        # Calculate validity period
        valid_from = timezone.now()
        valid_to = valid_from + timedelta(days=access_request.requested_duration_days)
        
        # Create grant
        grant = AccessGrant.objects.create(
            patient=access_request.patient,
            grantee_org=access_request.requester_org,
            access_request=access_request,
            scopes=access_request.scopes,
            valid_from=valid_from,
            valid_to=valid_to,
            created_by='patient'
        )
        
        # Update access request status
        access_request.status = 'approved'
        access_request.responded_at = timezone.now()
        access_request.save(update_fields=['status', 'responded_at'])
        
        # Log action
        AuditLog.objects.create(
            user=None,  # Patient action
            organization=access_request.requester_org,
            patient=access_request.patient,
            action='share',
            access_grant=grant,
            details={
                'access_request_id': str(access_request.id),
                'grant_id': str(grant.id),
                'scopes': grant.scopes,
                'valid_to': grant.valid_to.isoformat()
            }
        )
        
        return grant


class AccessGrantSerializer(serializers.ModelSerializer):
    """
    Serializer for access grants
    """
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    grantee_org_name = serializers.CharField(source='grantee_org.name', read_only=True)
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = AccessGrant
        fields = [
            'id', 'patient', 'patient_name',
            'grantee_org', 'grantee_org_name',
            'scopes', 'valid_from', 'valid_to', 'is_active',
            'is_whitelist', 'created_by',
            'last_accessed_at', 'access_count',
            'revoked_at', 'revocation_reason',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_accessed_at', 'access_count']
    
    def get_is_active(self, obj):
        return obj.is_active()


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for audit logs
    """
    user_name = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'user_name', 'organization', 'organization_name',
            'patient', 'patient_name',
            'action', 'action_display',
            'object_type', 'object_id',
            'ip_address', 'details',
            'created_at'
        ]
        read_only_fields = fields  # All fields are read-only
    
    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return 'Пациент'

