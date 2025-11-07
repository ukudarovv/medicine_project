"""
Tests for EHR API
"""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.org.models import Organization
from apps.patients.models import Patient
from apps.consent.models import AccessGrant
from apps.ehr.models import EHRRecord

User = get_user_model()


class EHRRecordTestCase(TestCase):
    """Test EHR record model"""
    
    def setUp(self):
        """Set up test data"""
        self.org = Organization.objects.create(name='Test Clinic')
        self.user = User.objects.create_user(
            username='doctor',
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
    
    def test_create_ehr_record(self):
        """Test creating EHR record"""
        record = EHRRecord.objects.create(
            patient=self.patient,
            organization=self.org,
            author=self.user,
            record_type='visit_note',
            title='Initial consultation',
            payload={
                'complaints': 'Headache',
                'diagnosis': 'Migraine',
                'treatment': 'Rest and medication'
            }
        )
        
        self.assertEqual(record.patient, self.patient)
        self.assertEqual(record.organization, self.org)
        self.assertFalse(record.is_external)
        self.assertEqual(record.version, 1)
    
    def test_external_record(self):
        """Test marking record as external"""
        org2 = Organization.objects.create(name='Other Clinic')
        
        record = EHRRecord.objects.create(
            patient=self.patient,
            organization=org2,
            author=self.user,
            record_type='visit_note',
            title='External consultation',
            payload={'note': 'Test'},
            is_external=True
        )
        
        self.assertTrue(record.is_external)
        self.assertEqual(record.organization, org2)
    
    def test_record_versioning(self):
        """Test record versioning"""
        record = EHRRecord.objects.create(
            patient=self.patient,
            organization=self.org,
            author=self.user,
            record_type='visit_note',
            title='Initial note',
            payload={'note': 'Version 1'}
        )
        
        # Create new version
        updated_payload = {'note': 'Version 2'}
        new_version = record.create_new_version(updated_payload, self.user)
        
        self.assertEqual(new_version.version, 2)
        self.assertEqual(new_version.previous_version, record)
        self.assertEqual(new_version.payload['note'], 'Version 2')
        self.assertEqual(record.payload['note'], 'Version 1')  # Original unchanged
    
    def test_soft_delete(self):
        """Test soft delete"""
        record = EHRRecord.objects.create(
            patient=self.patient,
            organization=self.org,
            author=self.user,
            record_type='diagnosis',
            title='Test diagnosis',
            payload={}
        )
        
        self.assertFalse(record.is_deleted)
        
        # Soft delete
        record.soft_delete()
        
        self.assertTrue(record.is_deleted)
        self.assertIsNotNone(record.deleted_at)


class EHRAccessControlTestCase(TestCase):
    """Test EHR access control with grants"""
    
    def setUp(self):
        """Set up test data"""
        self.org1 = Organization.objects.create(name='Clinic A')
        self.org2 = Organization.objects.create(name='Clinic B')
        
        self.user1 = User.objects.create_user(
            username='doctor1',
            password='test123',
            organization=self.org1,
            role='doctor'
        )
        self.user2 = User.objects.create_user(
            username='doctor2',
            password='test123',
            organization=self.org2,
            role='doctor'
        )
        
        self.patient = Patient.objects.create(
            organization=self.org1,
            first_name='Test',
            last_name='Patient',
            birth_date='1990-01-01',
            sex='M',
            phone='+77001234567'
        )
        
        # Create records in org1
        self.record1 = EHRRecord.objects.create(
            patient=self.patient,
            organization=self.org1,
            author=self.user1,
            record_type='visit_note',
            title='Record from Clinic A',
            payload={}
        )
    
    def test_own_records_access(self):
        """Test accessing own organization's records"""
        records = EHRRecord.objects.filter(
            patient=self.patient,
            organization=self.org1,
            is_deleted=False
        )
        
        self.assertEqual(records.count(), 1)
        self.assertEqual(records.first(), self.record1)
    
    def test_external_records_with_grant(self):
        """Test accessing external records with valid grant"""
        # Create grant
        grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org2,
            scopes=['read_records'],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )
        
        self.assertTrue(grant.is_active())
        self.assertTrue(grant.has_scope('read_records'))
        
        # User2 from org2 should now have access through grant
        # (Would be enforced in view/middleware)
    
    def test_write_scope(self):
        """Test write scope for external records"""
        grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org2,
            scopes=['read_records', 'write_records'],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )
        
        self.assertTrue(grant.has_scope('write_records'))
        
        # User2 can create records in patient's chart
        external_record = EHRRecord.objects.create(
            patient=self.patient,
            organization=self.org2,
            author=self.user2,
            record_type='diagnosis',
            title='External diagnosis',
            payload={},
            is_external=True
        )
        
        self.assertTrue(external_record.is_external)
        self.assertEqual(external_record.organization, self.org2)

