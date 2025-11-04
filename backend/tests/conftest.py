import pytest
from django.contrib.auth import get_user_model
from apps.org.models import Organization, Branch
from apps.staff.models import Employee
from apps.patients.models import Patient
from datetime import date

User = get_user_model()


@pytest.fixture
def organization(db):
    """Create test organization"""
    return Organization.objects.create(
        name='Test Clinic',
        sms_sender='TestClinic'
    )


@pytest.fixture
def branch(db, organization):
    """Create test branch"""
    return Branch.objects.create(
        organization=organization,
        name='Test Branch',
        address='Test Address',
        timezone='Asia/Almaty'
    )


@pytest.fixture
def admin_user(db, organization):
    """Create admin user"""
    return User.objects.create_user(
        username='admin',
        password='testpass123',
        email='admin@test.com',
        role='owner',
        organization=organization
    )


@pytest.fixture
def doctor_user(db, organization):
    """Create doctor user"""
    return User.objects.create_user(
        username='doctor',
        password='testpass123',
        email='doctor@test.com',
        role='doctor',
        organization=organization
    )


@pytest.fixture
def employee(db, organization):
    """Create test employee"""
    return Employee.objects.create(
        organization=organization,
        first_name='Test',
        last_name='Doctor',
        position='Врач',
        phone='+77011234567',
        hire_date=date(2023, 1, 1),
        color='#2196F3'
    )


@pytest.fixture
def patient(db, organization):
    """Create test patient"""
    return Patient.objects.create(
        organization=organization,
        first_name='Test',
        last_name='Patient',
        birth_date=date(1990, 1, 1),
        sex='M',
        phone='+77017654321'
    )


@pytest.fixture
def api_client():
    """Create API client"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, admin_user):
    """Create authenticated API client"""
    api_client.force_authenticate(user=admin_user)
    return api_client

