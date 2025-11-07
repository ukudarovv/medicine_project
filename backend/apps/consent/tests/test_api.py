"""
API endpoint tests for consent system
"""
from datetime import timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.org.models import Organization
from apps.patients.models import Patient
from apps.consent.models import AccessRequest, AccessGrant

User = get_user_model()


class PatientSearchAPITestCase(TestCase):
    """Test patient search API endpoint"""
    
    def setUp(self):
        self.org = Organization.objects.create(name='Test Clinic')
        self.user = User.objects.create_user(
            username='doctor',
            password='test123',
            organization=self.org,
            role='doctor'
        )
        self.patient = Patient.objects.create(
            organization=self.org,
            first_name='Тест',
            last_name='Пациентов',
            birth_date='1990-01-01',
            sex='M',
            phone='+77001234567'
        )
        self.patient.set_iin('900101300123')
        self.patient.save()
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_search_patient_by_iin_success(self):
        """Test successful patient search"""
        response = self.client.post('/api/v1/consent/search-patient/', {
            'iin': '900101300123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.patient.id)
        self.assertIn('fio_masked', response.data)
        self.assertIn('iin_masked', response.data)
    
    def test_search_patient_not_found(self):
        """Test patient not found"""
        response = self.client.post('/api/v1/consent/search-patient/', {
            'iin': '999999999999'
        })
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AccessRequestAPITestCase(TestCase):
    """Test access request API endpoints"""
    
    def setUp(self):
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
        self.patient.set_iin('900101300123')
        self.patient.save()
        
        self.client = APIClient()
    
    def test_create_access_request(self):
        """Test creating access request"""
        from apps.telegram_bot.models import PatientTelegramLink
        
        # Link patient to Telegram
        PatientTelegramLink.objects.create(
            patient=self.patient,
            telegram_user_id=123456789
        )
        
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.post('/api/v1/consent/access-requests/', {
            'patient_iin': '900101300123',
            'scopes': ['read_summary', 'read_records'],
            'reason': 'Medical consultation',
            'requested_duration_days': 30
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending')
        self.assertIn('id', response.data)
    
    def test_list_access_requests(self):
        """Test listing access requests"""
        # Create request
        AccessRequest.objects.create(
            patient=self.patient,
            requester_org=self.org2,
            requester_user=self.user2,
            scopes=['read_records'],
            reason='Test'
        )
        
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.get('/api/v1/consent/access-requests/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 1)


class AccessGrantAPITestCase(TestCase):
    """Test access grant API endpoints"""
    
    def setUp(self):
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
        
        self.grant = AccessGrant.objects.create(
            patient=self.patient,
            grantee_org=self.org,
            scopes=['read_records'],
            valid_from=timezone.now(),
            valid_to=timezone.now() + timedelta(days=30)
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_list_grants(self):
        """Test listing access grants"""
        response = self.client.get('/api/v1/consent/grants/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        self.assertGreaterEqual(len(results), 1)
    
    def test_revoke_grant(self):
        """Test revoking access grant"""
        response = self.client.post(
            f'/api/v1/consent/grants/{self.grant.id}/revoke/',
            {'reason': 'Test revocation'}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify grant is revoked
        self.grant.refresh_from_db()
        self.assertIsNotNone(self.grant.revoked_at)
        self.assertFalse(self.grant.is_active())

