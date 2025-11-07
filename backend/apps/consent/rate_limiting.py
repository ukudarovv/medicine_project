"""
Rate limiting for consent system using Redis
"""
import hashlib
from datetime import timedelta
from django.core.cache import cache
from django.conf import settings


class ConsentRateLimiter:
    """
    Rate limiter for consent access requests
    """
    
    @staticmethod
    def get_key(org_id, patient_id):
        """Generate Redis key for rate limiting"""
        return f"consent:rate:{org_id}:{patient_id}"
    
    @staticmethod
    def check_rate_limit(org_id, patient_id):
        """
        Check if organization has exceeded rate limit for this patient
        
        Args:
            org_id: Organization ID
            patient_id: Patient ID
            
        Returns:
            dict with keys:
                - allowed (bool): Whether request is allowed
                - count (int): Current request count
                - limit (int): Maximum allowed requests
                - reset_in (int): Seconds until reset
        """
        key = ConsentRateLimiter.get_key(org_id, patient_id)
        limit = getattr(settings, 'CONSENT_RATE_LIMIT_PER_DAY', 3)
        ttl = 86400  # 24 hours in seconds
        
        # Get current count
        count = cache.get(key, 0)
        
        if count >= limit:
            # Get TTL for key (Redis specific, fallback to default TTL)
            try:
                reset_in = cache.ttl(key) if hasattr(cache, 'ttl') else ttl
            except (AttributeError, TypeError):
                reset_in = ttl
            return {
                'allowed': False,
                'count': count,
                'limit': limit,
                'reset_in': reset_in
            }
        
        return {
            'allowed': True,
            'count': count,
            'limit': limit,
            'reset_in': ttl
        }
    
    @staticmethod
    def increment(org_id, patient_id):
        """
        Increment rate limit counter
        
        Args:
            org_id: Organization ID
            patient_id: Patient ID
        """
        key = ConsentRateLimiter.get_key(org_id, patient_id)
        ttl = 86400  # 24 hours
        
        count = cache.get(key, 0)
        cache.set(key, count + 1, ttl)
    
    @staticmethod
    def get_denial_count_key(org_id, patient_id):
        """Generate Redis key for denial tracking"""
        return f"consent:denials:{org_id}:{patient_id}"
    
    @staticmethod
    def check_denial_lockout(org_id, patient_id):
        """
        Check if organization is locked out due to repeated denials
        
        Args:
            org_id: Organization ID
            patient_id: Patient ID
            
        Returns:
            dict with keys:
                - locked_out (bool): Whether organization is locked out
                - denials (int): Number of denials
                - reset_in (int): Seconds until lockout reset
        """
        key = ConsentRateLimiter.get_denial_count_key(org_id, patient_id)
        max_denials = 3
        lockout_duration = 3600  # 1 hour
        
        denials = cache.get(key, 0)
        
        if denials >= max_denials:
            # Get TTL for key (Redis specific, fallback to default duration)
            try:
                reset_in = cache.ttl(key) if hasattr(cache, 'ttl') else lockout_duration
            except (AttributeError, TypeError):
                reset_in = lockout_duration
            return {
                'locked_out': True,
                'denials': denials,
                'reset_in': reset_in
            }
        
        return {
            'locked_out': False,
            'denials': denials,
            'reset_in': 0
        }
    
    @staticmethod
    def record_denial(org_id, patient_id):
        """
        Record a denial for lockout tracking
        
        Args:
            org_id: Organization ID
            patient_id: Patient ID
        """
        key = ConsentRateLimiter.get_denial_count_key(org_id, patient_id)
        lockout_duration = 3600  # 1 hour
        
        denials = cache.get(key, 0)
        cache.set(key, denials + 1, lockout_duration)


class ConsentFraudDetector:
    """
    Anti-fraud detection for consent system
    """
    
    @staticmethod
    def check_suspicious_activity(user, org, patient_id, action):
        """
        Check for suspicious activity patterns
        
        Args:
            user: User object
            org: Organization object
            patient_id: Patient ID
            action: Action type (request, read, write)
            
        Returns:
            dict with keys:
                - suspicious (bool): Whether activity is suspicious
                - reasons (list): List of reasons
                - severity (str): low, medium, high
        """
        reasons = []
        severity = 'low'
        
        # Check 1: Mass requests from single user
        if action == 'request':
            user_key = f"fraud:requests:user:{user.id}"
            user_count = cache.get(user_key, 0)
            
            if user_count > 10:  # More than 10 requests in an hour
                reasons.append(f'Массовые запросы от пользователя {user.username}')
                severity = 'high'
            
            # Increment counter
            cache.set(user_key, user_count + 1, 3600)
        
        # Check 2: Night-time requests (00:00 - 06:00)
        from django.utils import timezone
        now = timezone.now()
        hour = now.hour
        
        if 0 <= hour < 6:
            reasons.append('Запрос в ночное время (00:00-06:00)')
            if severity == 'low':
                severity = 'medium'
        
        # Check 3: Rapid consecutive requests to same patient
        if action == 'request':
            rapid_key = f"fraud:rapid:org:{org.id}:patient:{patient_id}"
            rapid_count = cache.get(rapid_key, 0)
            
            if rapid_count > 0:
                reasons.append('Повторный запрос к тому же пациенту за короткий период')
                if severity != 'high':
                    severity = 'medium'
            
            # Set flag for 10 minutes
            cache.set(rapid_key, rapid_count + 1, 600)
        
        # Check 4: High access frequency
        if action in ['read', 'write']:
            access_key = f"fraud:access:user:{user.id}"
            access_count = cache.get(access_key, 0)
            
            if access_count > 50:  # More than 50 accesses in an hour
                reasons.append(f'Высокая частота обращений: {access_count}/час')
                severity = 'high'
            
            cache.set(access_key, access_count + 1, 3600)
        
        is_suspicious = len(reasons) > 0
        
        return {
            'suspicious': is_suspicious,
            'reasons': reasons,
            'severity': severity
        }
    
    @staticmethod
    def log_suspicious_activity(user, org, patient_id, activity_data):
        """
        Log suspicious activity for review
        
        Args:
            user: User object
            org: Organization object
            patient_id: Patient ID
            activity_data: Dict with suspicious activity details
        """
        from apps.consent.models import AuditLog
        from apps.patients.models import Patient
        
        try:
            patient = Patient.objects.get(id=patient_id)
            
            AuditLog.objects.create(
                user=user,
                organization=org,
                patient=patient,
                action='request',  # or other action
                details={
                    'fraud_detected': True,
                    'suspicious_activity': activity_data,
                    'timestamp': timezone.now().isoformat()
                }
            )
        except Patient.DoesNotExist:
            pass

