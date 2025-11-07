"""
Integration tests for complete consent flow
Tests the entire journey from request to access
"""
from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.org.models import Organization, Branch
from apps.patients.models import Patient
from apps.telegram_bot.models import PatientTelegramLink
from apps.consent.models import AccessRequest, ConsentToken, AccessGrant, AuditLog
from apps.ehr.models import EHRRecord

User = get_user_model()


class E2EConsentFlowTestCase(TestCase):
    """
    End-to-end test of complete consent flow
    """
    
    def setUp(self):
        """Set up complete test environment"""
        # Organizations
        self.org_a = Organization.objects.create(name='Clinic A')
        self.org_b = Organization.objects.create(name='Clinic B')
        
        self.branch_a = Branch.objects.create(
            organization=self.org_a,
            name='Branch A1'
        )
        self.branch_b = Branch.objects.create(
            organization=self.org_b,
            name='Branch B1'
        )
        
        # Users
        self.doctor_a = User.objects.create_user(
            username='doctor_a',
            email='a@clinic-a.kz',
            password='test123',
            organization=self.org_a,
            role='doctor'
        )
        
        self.doctor_b = User.objects.create_user(
            username='doctor_b',
            email='b@clinic-b.kz',
            password='test123',
            organization=self.org_b,
            role='doctor'
        )
        
        # Patient in Org A
        self.patient = Patient.objects.create(
            organization=self.org_a,
            first_name='Алия',
            last_name='Смагулова',
            birth_date='1990-01-01',
            sex='F',
            phone='+77771234567'
        )
        self.patient.set_iin('900101450789')
        self.patient.save()
        
        # Link Telegram
        self.telegram_link = PatientTelegramLink.objects.create(
            patient=self.patient,
            telegram_user_id=123456789,
            telegram_username='aliya_test',
            language='ru'
        )
        
        # Create medical records in Org A
        self.record_a = EHRRecord.objects.create(
            patient=self.patient,
            organization=self.org_a,
            author=self.doctor_a,
            record_type='visit_note',
            title='Initial consultation',
            payload={'diagnosis': 'Healthy'}
        )
        
        # API client
        self.client = Client()
    
    def test_complete_flow_approve(self):
        """
        Test complete flow: request → OTP → approve → access
        """
        # Step 1: Doctor B requests access to Patient (from Org A)
        access_request = AccessRequest.objects.create(
            patient=self.patient,
            requester_org=self.org_b,
            requester_user=self.doctor_b,
            scopes=['read_summary', 'read_records'],
            reason='Consultation',
            requested_duration_days=30
        )
        
        self.assertEqual(access_request.status, 'pending')
        
        # Step 2: OTP token generated
        otp_code = ConsentToken.generate_otp_code()
        otp_hash = ConsentToken.hash_otp(otp_code)
        
        token = ConsentToken.objects.create(
            access_request=access_request,
            otp_code_hash=otp_hash,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # Step 3: Patient approves (verifies OTP)
        is_valid = token.verify_otp(otp_code)
        self.assertTrue(is_valid)
        self.assertIsNotNone(token.used_at)
        
        # Step 4: Create grant
        grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org_b,
            access_request=access_request,
            scopes=access_request.scopes,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )
        
        # Update request status
        access_request.status = 'approved'
        access_request.responded_at = timezone.now()
        access_request.save()
        
        # Step 5: Verify access
        self.assertTrue(grant.is_active())
        self.assertTrue(grant.has_scope('read_records'))
        
        # Step 6: Doctor B can now access records
        # (In view, this would be checked by middleware)
        accessible_records = EHRRecord.objects.filter(
            patient=self.patient,
            is_deleted=False
        )
        
        self.assertGreater(accessible_records.count(), 0)
        
        # Step 7: Track access
        grant.track_access()
        self.assertEqual(grant.access_count, 1)
        self.assertIsNotNone(grant.last_accessed_at)
        
        # Step 8: Create audit log
        audit_log = AuditLog.objects.create(
            user=self.doctor_b,
            organization=self.org_b,
            patient=self.patient,
            action='read',
            access_grant=grant,
            object_type='EHRRecord',
            object_id=str(self.record_a.id)
        )
        
        self.assertEqual(audit_log.action, 'read')
        
        # Verify audit log count
        total_logs = AuditLog.objects.filter(patient=self.patient).count()
        self.assertGreaterEqual(total_logs, 1)
    
    def test_complete_flow_deny(self):
        """
        Test complete flow: request → deny
        """
        # Step 1: Create request
        access_request = AccessRequest.objects.create(
            patient=self.patient,
            requester_org=self.org_b,
            requester_user=self.doctor_b,
            scopes=['read_records'],
            reason='Consultation',
            requested_duration_days=7
        )
        
        # Step 2: Patient denies
        access_request.status = 'denied'
        access_request.responded_at = timezone.now()
        access_request.save()
        
        # Step 3: No grant should exist
        grant_exists = AccessGrant.objects.filter(
            access_request=access_request
        ).exists()
        
        self.assertFalse(grant_exists)
        
        # Step 4: Log denial
        AuditLog.objects.create(
            user=None,  # Patient action
            organization=self.org_b,
            patient=self.patient,
            action='deny',
            details={'request_id': str(access_request.id)}
        )
        
        # Verify denial logged
        denial_logs = AuditLog.objects.filter(
            patient=self.patient,
            action='deny'
        )
        self.assertEqual(denial_logs.count(), 1)
    
    def test_external_record_creation(self):
        """
        Test creating external record with write scope
        """
        # Step 1: Create grant with write scope
        grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org_b,
            scopes=['read_records', 'write_records'],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )
        
        # Step 2: Doctor B creates record in Patient's chart
        external_record = EHRRecord.objects.create(
            patient=self.patient,
            organization=self.org_b,  # From Org B
            author=self.doctor_b,
            record_type='diagnosis',
            title='External diagnosis from Clinic B',
            payload={'diagnosis': 'Test diagnosis'},
            is_external=True
        )
        
        # Step 3: Verify record
        self.assertTrue(external_record.is_external)
        self.assertEqual(external_record.organization, self.org_b)
        
        # Step 4: Both doctors can see this record
        all_records = EHRRecord.objects.filter(
            patient=self.patient,
            is_deleted=False
        )
        
        # Should have: 1 from Org A + 1 from Org B
        self.assertEqual(all_records.count(), 2)
        
        # Step 5: Log creation
        AuditLog.objects.create(
            user=self.doctor_b,
            organization=self.org_b,
            patient=self.patient,
            action='write',
            access_grant=grant,
            object_type='EHRRecord',
            object_id=str(external_record.id)
        )
    
    def test_grant_lifecycle(self):
        """
        Test complete grant lifecycle: create → use → revoke
        """
        # Create grant
        grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org_b,
            scopes=['read_records'],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )
        
        # Grant should be active
        self.assertTrue(grant.is_active())
        
        # Track multiple accesses
        for i in range(5):
            grant.track_access()
        
        self.assertEqual(grant.access_count, 5)
        
        # Revoke grant
        grant.revoke(user=self.doctor_a, reason='Patient request')
        
        # Grant should no longer be active
        self.assertFalse(grant.is_active())
        self.assertIsNotNone(grant.revoked_at)
        self.assertEqual(grant.revoked_by, self.doctor_a)
        
        # Log revocation
        AuditLog.objects.create(
            user=self.doctor_a,
            organization=self.org_a,
            patient=self.patient,
            action='revoke',
            access_grant=grant
        )
        
        # Verify revocation logged
        revoke_logs = AuditLog.objects.filter(
            patient=self.patient,
            action='revoke'
        )
        self.assertGreaterEqual(revoke_logs.count(), 1)
    
    def test_whitelist_long_term_access(self):
        """
        Test whitelist (long-term trusted) access
        """
        # Patient creates whitelist for Org B (e.g., family doctor)
        whitelist_grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org_b,
            scopes=['read_summary', 'read_records', 'read_images'],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=180),  # 6 months
            is_whitelist=True,
            created_by='patient'
        )
        
        # Verify whitelist properties
        self.assertTrue(whitelist_grant.is_whitelist)
        self.assertTrue(whitelist_grant.is_active())
        self.assertEqual(whitelist_grant.created_by, 'patient')
        
        # Whitelist grants should have longer duration
        duration = whitelist_grant.valid_to - whitelist_grant.valid_from
        self.assertGreaterEqual(duration.days, 180)
        
        # Can be revoked anytime
        whitelist_grant.revoke(reason='Changed doctor')
        self.assertFalse(whitelist_grant.is_active())
    
    def test_versioning_workflow(self):
        """
        Test EHR record versioning when edited
        """
        # Original record
        original_record = EHRRecord.objects.create(
            patient=self.patient,
            organization=self.org_a,
            author=self.doctor_a,
            record_type='visit_note',
            title='Visit note',
            payload={'note': 'Original version', 'diagnosis': 'Healthy'}
        )
        
        self.assertEqual(original_record.version, 1)
        
        # Edit creates new version
        updated_payload = {
            'note': 'Updated version',
            'diagnosis': 'Healthy',
            'additional_note': 'Added follow-up'
        }
        
        new_version = original_record.create_new_version(
            updated_payload,
            self.doctor_a
        )
        
        # Verify versioning
        self.assertEqual(new_version.version, 2)
        self.assertEqual(new_version.previous_version, original_record)
        self.assertEqual(new_version.payload['note'], 'Updated version')
        
        # Original unchanged
        original_record.refresh_from_db()
        self.assertEqual(original_record.payload['note'], 'Original version')


class RateLimitingIntegrationTestCase(TestCase):
    """
    Integration tests for rate limiting
    """
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(name='Test Clinic')
        self.user = User.objects.create_user(
            username='test_doctor',
            password='test123',
            organization=self.org,
            role='doctor'
        )
        self.patient = Patient.objects.create(
            organization=self.org,
            first_name='Test',
            last_name='Patient',
            birth_date='1990-01-01',
            sex='M',
            phone='+77001234567'
        )
    
    def test_rate_limit_enforcement(self):
        """
        Test that rate limiting works correctly
        """
        from apps.consent.rate_limiting import ConsentRateLimiter
        from django.core.cache import cache
        
        # Clear any existing limits
        cache.clear()
        
        org_id = self.org.id
        patient_id = self.patient.id
        
        # First 3 requests should be allowed
        for i in range(3):
            check = ConsentRateLimiter.check_rate_limit(org_id, patient_id)
            self.assertTrue(check['allowed'], f"Request {i+1} should be allowed")
            ConsentRateLimiter.increment(org_id, patient_id)
        
        # 4th request should be blocked
        check = ConsentRateLimiter.check_rate_limit(org_id, patient_id)
        self.assertFalse(check['allowed'], "4th request should be blocked")
        self.assertEqual(check['count'], 3)
        self.assertEqual(check['limit'], 3)
    
    def test_denial_lockout(self):
        """
        Test that denial lockout works correctly
        """
        from apps.consent.rate_limiting import ConsentRateLimiter
        from django.core.cache import cache
        
        cache.clear()
        
        org_id = self.org.id
        patient_id = self.patient.id
        
        # First 2 denials
        for i in range(2):
            check = ConsentRateLimiter.check_denial_lockout(org_id, patient_id)
            self.assertFalse(check['locked_out'])
            ConsentRateLimiter.record_denial(org_id, patient_id)
        
        # 3rd denial should trigger lockout
        ConsentRateLimiter.record_denial(org_id, patient_id)
        
        check = ConsentRateLimiter.check_denial_lockout(org_id, patient_id)
        self.assertTrue(check['locked_out'])
        self.assertEqual(check['denials'], 3)


class FraudDetectionIntegrationTestCase(TestCase):
    """
    Integration tests for fraud detection
    """
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(name='Test Clinic')
        self.user = User.objects.create_user(
            username='test_doctor',
            password='test123',
            organization=self.org,
            role='doctor'
        )
        self.patient = Patient.objects.create(
            organization=self.org,
            first_name='Test',
            last_name='Patient',
            birth_date='1990-01-01',
            sex='M',
            phone='+77001234567'
        )
    
    def test_fraud_detection_mass_requests(self):
        """
        Test detection of mass requests
        """
        from apps.consent.rate_limiting import ConsentFraudDetector
        from django.core.cache import cache
        
        cache.clear()
        
        # Simulate 11 requests in an hour (exceeds threshold of 10)
        for i in range(11):
            fraud_check = ConsentFraudDetector.check_suspicious_activity(
                self.user,
                self.org,
                self.patient.id,
                'request'
            )
        
        # 11th request should be flagged
        self.assertTrue(fraud_check['suspicious'])
        self.assertIn('Массовые запросы', fraud_check['reasons'][0])
        self.assertEqual(fraud_check['severity'], 'high')


class AuditLogIntegrationTestCase(TestCase):
    """
    Integration tests for audit logging
    """
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(name='Test Clinic')
        self.user = User.objects.create_user(
            username='test_doctor',
            password='test123',
            organization=self.org,
            role='doctor'
        )
        self.patient = Patient.objects.create(
            organization=self.org,
            first_name='Test',
            last_name='Patient',
            birth_date='1990-01-01',
            sex='M',
            phone='+77001234567'
        )
    
    def test_audit_trail_completeness(self):
        """
        Test that complete audit trail is maintained
        """
        # Action 1: Request
        request_log = AuditLog.objects.create(
            user=self.user,
            organization=self.org,
            patient=self.patient,
            action='request',
            details={'reason': 'Test'}
        )
        
        # Action 2: Share
        share_log = AuditLog.objects.create(
            user=None,  # Patient action
            organization=self.org,
            patient=self.patient,
            action='share',
            details={'scopes': ['read_records']}
        )
        
        # Action 3: Read
        read_log = AuditLog.objects.create(
            user=self.user,
            organization=self.org,
            patient=self.patient,
            action='read',
            object_type='EHRRecord',
            object_id='123'
        )
        
        # Verify all logged
        logs = AuditLog.objects.filter(patient=self.patient).order_by('created_at')
        self.assertEqual(logs.count(), 3)
        
        actions = [log.action for log in logs]
        self.assertEqual(actions, ['request', 'share', 'read'])
    
    def test_patient_audit_view(self):
        """
        Test patient can view their own audit trail
        """
        # Create various actions
        for action in ['request', 'share', 'read', 'read', 'write']:
            AuditLog.objects.create(
                user=self.user if action != 'share' else None,
                organization=self.org,
                patient=self.patient,
                action=action
            )
        
        # Patient should see all actions
        patient_logs = AuditLog.objects.filter(patient=self.patient)
        self.assertEqual(patient_logs.count(), 5)
        
        # Group by action
        actions_count = {}
        for log in patient_logs:
            actions_count[log.action] = actions_count.get(log.action, 0) + 1
        
        self.assertEqual(actions_count['read'], 2)
        self.assertEqual(actions_count['write'], 1)

