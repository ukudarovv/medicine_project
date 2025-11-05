"""
API tests for Telegram Bot
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from apps.patients.models import Patient
from apps.org.models import Organization
from apps.telegram_bot.models import PatientTelegramLink
from django.conf import settings


class TelegramBotAPITest(TestCase):
    """Test Telegram Bot API endpoints"""
    
    def setUp(self):
        """Set up test client and auth"""
        self.client = APIClient()
        self.api_secret = settings.TELEGRAM_BOT_API_SECRET
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.api_secret}'}
        
        # Create test organization
        self.organization = Organization.objects.create(
            name="Test Clinic",
            phone="+77771234567"
        )
    
    def test_patient_upsert_create(self):
        """Test creating new patient via bot"""
        url = reverse('telegram_bot:patient-upsert')
        data = {
            'telegram_user_id': 123456789,
            'telegram_username': 'testuser',
            'language': 'ru',
            'first_name': 'Тест',
            'last_name': 'Тестов',
            'phone': '+77771234567',
            'birth_date': '1990-01-01',
            'sex': 'M',
            'organization_id': self.organization.id
        }
        
        response = self.client.post(url, data, **self.headers, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['created'])
        self.assertIn('patient_id', response.data)
    
    def test_patient_upsert_update(self):
        """Test updating existing patient"""
        # Create patient
        patient = Patient.objects.create(
            organization=self.organization,
            first_name='Старое',
            last_name='Имя',
            birth_date='1990-01-01',
            sex='M',
            phone='+77771234567'
        )
        
        PatientTelegramLink.objects.create(
            patient=patient,
            telegram_user_id=123456789
        )
        
        url = reverse('telegram_bot:patient-upsert')
        data = {
            'telegram_user_id': 123456789,
            'first_name': 'Новое',
            'last_name': 'Имя',
            'phone': '+77771234567',
            'birth_date': '1990-01-01',
            'sex': 'M',
            'organization_id': self.organization.id
        }
        
        response = self.client.post(url, data, **self.headers, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['created'])
        
        # Check updated
        patient.refresh_from_db()
        self.assertEqual(patient.first_name, 'Новое')
    
    def test_verify_iin(self):
        """Test IIN verification"""
        url = reverse('telegram_bot:verify-iin')
        data = {'iin': '960825400123'}
        
        response = self.client.post(url, data, **self.headers, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('valid', response.data)
    
    def test_authentication_required(self):
        """Test that API requires authentication"""
        url = reverse('telegram_bot:patient-upsert')
        data = {'telegram_user_id': 123}
        
        # Without auth header
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_patient_by_telegram(self):
        """Test getting patient by telegram ID"""
        # Create patient with telegram link
        patient = Patient.objects.create(
            organization=self.organization,
            first_name='Тест',
            last_name='Тестов',
            birth_date='1990-01-01',
            sex='M',
            phone='+77771234567'
        )
        
        PatientTelegramLink.objects.create(
            patient=patient,
            telegram_user_id=123456789,
            language='ru'
        )
        
        url = reverse('telegram_bot:patient-by-telegram', kwargs={'telegram_user_id': 123456789})
        
        response = self.client.get(url, **self.headers)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['telegram_user_id'], 123456789)
        self.assertIn('patient_full_name', response.data)


class TelegramBotModelsTest(TestCase):
    """Test Telegram Bot models"""
    
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Clinic",
            phone="+77771234567"
        )
        
        self.patient = Patient.objects.create(
            organization=self.organization,
            first_name='Тест',
            last_name='Тестов',
            birth_date='1990-01-01',
            sex='M',
            phone='+77771234567'
        )
    
    def test_patient_telegram_link_creation(self):
        """Test creating PatientTelegramLink"""
        link = PatientTelegramLink.objects.create(
            patient=self.patient,
            telegram_user_id=123456789,
            telegram_username='testuser',
            language='ru'
        )
        
        self.assertEqual(link.patient, self.patient)
        self.assertEqual(link.telegram_user_id, 123456789)
        self.assertEqual(link.language, 'ru')
        self.assertTrue(link.is_active)
    
    def test_bot_feedback_low_score(self):
        """Test BotFeedback low score flag"""
        from apps.telegram_bot.models import BotFeedback
        from apps.calendar.models import Appointment
        from apps.services.models import Service
        from apps.staff.models import Employee
        from apps.org.models import Branch
        
        # Create dependencies (simplified)
        branch = Branch.objects.create(
            organization=self.organization,
            name="Test Branch"
        )
        
        service = Service.objects.create(
            organization=self.organization,
            name="Test Service",
            price=1000
        )
        
        employee = Employee.objects.create(
            organization=self.organization,
            first_name="Test",
            last_name="Doctor",
            role="doctor"
        )
        
        appointment = Appointment.objects.create(
            patient=self.patient,
            employee=employee,
            service=service,
            branch=branch,
            date='2025-11-10',
            time_from='10:00',
            time_to='10:30',
            status='completed'
        )
        
        link = PatientTelegramLink.objects.create(
            patient=self.patient,
            telegram_user_id=123456789
        )
        
        # Low score
        feedback = BotFeedback.objects.create(
            appointment=appointment,
            patient_telegram_link=link,
            score=5,
            comment="Not great"
        )
        
        self.assertTrue(feedback.is_low_score)
        
        # High score
        feedback2 = BotFeedback.objects.create(
            appointment=appointment,
            patient_telegram_link=link,
            score=9,
            comment="Excellent"
        )
        
        self.assertFalse(feedback2.is_low_score)

