import pytest
from apps.patients.models import Patient


@pytest.mark.django_db
class TestPatients:
    """Test patient endpoints"""
    
    def test_list_patients(self, authenticated_client, patient):
        """Test listing patients"""
        response = authenticated_client.get('/api/v1/patients/patients')
        
        assert response.status_code == 200
        assert len(response.data['results']) > 0
    
    def test_create_patient(self, authenticated_client, organization):
        """Test creating patient"""
        data = {
            'organization': organization.id,
            'first_name': 'New',
            'last_name': 'Patient',
            'birth_date': '1995-05-15',
            'sex': 'F',
            'phone': '+77019999999'
        }
        
        response = authenticated_client.post('/api/v1/patients/patients', data)
        
        assert response.status_code == 201
        assert response.data['first_name'] == 'New'
        assert response.data['last_name'] == 'Patient'
    
    def test_patient_search_by_phone(self, authenticated_client, patient):
        """Test patient search by phone"""
        response = authenticated_client.post('/api/v1/patients/patients/search', {
            'phone': patient.phone
        })
        
        assert response.status_code == 200
        assert response.data['found'] is True
        assert response.data['count'] > 0
    
    def test_patient_full_name(self, patient):
        """Test patient full_name property"""
        assert patient.full_name == 'Patient Test'
    
    def test_patient_age(self, patient):
        """Test patient age calculation"""
        assert patient.age > 30

