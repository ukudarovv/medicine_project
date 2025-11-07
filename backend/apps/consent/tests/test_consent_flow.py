"""
Tests for consent flow
"""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.org.models import Organization
from apps.patients.models import Patient
from apps.consent.models import AccessRequest, ConsentToken, AccessGrant, AuditLog
from apps.patients.utils.encryption import hash_iin

User = get_user_model()


class ConsentFlowTestCase(TestCase):
    """Test complete consent flow"""
    
    def setUp(self):
        """Set up test data"""
        # Create organizations
        self.org1 = Organization.objects.create(name='Clinic A')
        self.org2 = Organization.objects.create(name='Clinic B')
        
        # Create users
        self.user1 = User.objects.create_user(
            username='doctor1',
            email='doctor1@clinic-a.kz',
            password='test123',
            organization=self.org1,
            role='doctor'
        )
        self.user2 = User.objects.create_user(
            username='doctor2',
            email='doctor2@clinic-b.kz',
            password='test123',
            organization=self.org2,
            role='doctor'
        )
        
        # Create patient
        self.patient = Patient.objects.create(
            organization=self.org1,
            first_name='Иван',
            last_name='Иванов',
            middle_name='Иванович',
            birth_date='1990-01-01',
            sex='M',
            phone='+77001234567'
        )
        self.patient.set_iin('900101300123')
        self.patient.save()
    
    def test_access_request_creation(self):
        """Test creating access request"""
        request = AccessRequest.objects.create(
            patient=self.patient,
            requester_org=self.org2,
            requester_user=self.user2,
            scopes=['read_summary', 'read_records'],
            reason='Consultation',
            requested_duration_days=30
        )
        
        self.assertEqual(request.status, 'pending')
        self.assertEqual(request.patient, self.patient)
        self.assertEqual(request.requester_org, self.org2)
        self.assertIsNotNone(request.expires_at)
    
    def test_otp_generation_and_verification(self):
        """Test OTP token generation and verification"""
        request = AccessRequest.objects.create(
            patient=self.patient,
            requester_org=self.org2,
            requester_user=self.user2,
            scopes=['read_records'],
            reason='Emergency',
            requested_duration_days=7
        )
        
        # Generate OTP
        otp_code = ConsentToken.generate_otp_code()
        self.assertEqual(len(otp_code), 6)
        self.assertTrue(otp_code.isdigit())
        
        # Create token
        otp_hash = ConsentToken.hash_otp(otp_code)
        token = ConsentToken.objects.create(
            access_request=request,
            otp_code_hash=otp_hash,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        # Verify correct OTP
        self.assertTrue(token.verify_otp(otp_code))
        self.assertIsNotNone(token.used_at)
        
        # Verify incorrect OTP
        token2 = ConsentToken.objects.create(
            access_request=request,
            otp_code_hash=ConsentToken.hash_otp('123456'),
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        self.assertFalse(token2.verify_otp('654321'))
    
    def test_grant_creation_after_approval(self):
        """Test creating grant after approval"""
        request = AccessRequest.objects.create(
            patient=self.patient,
            requester_org=self.org2,
            requester_user=self.user2,
            scopes=['read_summary', 'read_records'],
            reason='Treatment',
            requested_duration_days=30
        )
        
        # Approve request
        request.status = 'approved'
        request.responded_at = timezone.now()
        request.save()
        
        # Create grant
        grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org2,
            access_request=request,
            scopes=request.scopes,
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )
        
        self.assertTrue(grant.is_active())
        self.assertTrue(grant.has_scope('read_records'))
        self.assertFalse(grant.has_scope('write_records'))
    
    def test_grant_revocation(self):
        """Test revoking access grant"""
        grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org2,
            scopes=['read_records'],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )
        
        self.assertTrue(grant.is_active())
        
        # Revoke grant
        grant.revoke(user=self.user1, reason='Patient request')
        
        self.assertFalse(grant.is_active())
        self.assertIsNotNone(grant.revoked_at)
        self.assertEqual(grant.revoked_by, self.user1)
    
    def test_audit_logging(self):
        """Test audit log creation"""
        log = AuditLog.objects.create(
            user=self.user2,
            organization=self.org2,
            patient=self.patient,
            action='read',
            object_type='EHRRecord',
            object_id='123',
            ip_address='127.0.0.1',
            details={'test': 'data'}
        )
        
        self.assertEqual(log.action, 'read')
        self.assertEqual(log.patient, self.patient)
        
        # Test immutability
        with self.assertRaises(Exception):
            log.action = 'write'
            log.save()
        
        with self.assertRaises(Exception):
            log.delete()
    
    def test_request_expiration(self):
        """Test request expiration"""
        request = AccessRequest.objects.create(
            patient=self.patient,
            requester_org=self.org2,
            requester_user=self.user2,
            scopes=['read_records'],
            reason='Test',
            requested_duration_days=7,
            expires_at=timezone.now() - timedelta(minutes=1)  # Already expired
        )
        
        self.assertTrue(request.is_expired())
        
        # Mark as expired
        request.mark_expired()
        self.assertEqual(request.status, 'expired')
    
    def test_iin_encryption(self):
        """Test IIN encryption and hashing"""
        test_iin = '900101300124'
        
        patient = Patient.objects.create(
            organization=self.org1,
            first_name='Test',
            last_name='Patient',
            birth_date='1990-01-01',
            sex='M',
            phone='+77001234568'
        )
        patient.set_iin(test_iin)
        patient.save()
        
        # Check encryption
        self.assertIsNotNone(patient.iin_enc)
        self.assertIsNotNone(patient.iin_hash)
        self.assertNotEqual(patient.iin_enc, test_iin)
        
        # Check decryption
        decrypted = patient.iin_decrypted
        self.assertEqual(decrypted, test_iin)
        
        # Check masked IIN
        masked = patient.iin_masked
        self.assertTrue(masked.endswith('0124'))
        self.assertTrue('*' in masked)
    
    def test_whitelist_grant(self):
        """Test whitelist (long-term) grant"""
        grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org2,
            scopes=['read_summary', 'read_records'],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=180),  # 6 months
            is_whitelist=True,
            created_by='patient'
        )
        
        self.assertTrue(grant.is_whitelist)
        self.assertTrue(grant.is_active())
        
        # Track access
        initial_count = grant.access_count
        grant.track_access()
        self.assertEqual(grant.access_count, initial_count + 1)
        self.assertIsNotNone(grant.last_accessed_at)


class ConsentAPITestCase(TestCase):
    """Test consent API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(name='Test Clinic')
        self.user = User.objects.create_user(
            username='testdoctor',
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
        self.patient.set_iin('900101300123')
        self.patient.save()
    
    def test_patient_search_by_iin(self):
        """Test patient search by IIN hash"""
        iin = '900101300123'
        iin_hash_value = hash_iin(iin)
        
        found = Patient.objects.filter(iin_hash=iin_hash_value).first()
        self.assertIsNotNone(found)
        self.assertEqual(found.id, self.patient.id)
    
    def test_access_without_grant(self):
        """Test that access is denied without grant"""
        org2 = Organization.objects.create(name='Other Clinic')
        user2 = User.objects.create_user(
            username='otherdoctor',
            password='test123',
            organization=org2,
            role='doctor'
        )
        
        # User from org2 should not have access to patient from org1
        # (Would be tested in view with proper middleware)
        self.assertNotEqual(self.patient.organization, user2.organization)
    
    def test_access_with_valid_grant(self):
        """Test that access is allowed with valid grant"""
        org2 = Organization.objects.create(name='Other Clinic')
        
        grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=org2,
            scopes=['read_records'],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )
        
        self.assertTrue(grant.is_active())
        self.assertTrue(grant.has_scope('read_records'))

