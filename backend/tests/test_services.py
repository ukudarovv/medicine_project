import pytest
from apps.services.models import ServiceCategory, Service


@pytest.mark.django_db
class TestServices:
    """Test service endpoints"""
    
    def test_create_category(self, authenticated_client, organization):
        """Test creating service category"""
        data = {
            'organization': organization.id,
            'name': 'Test Category',
            'code': 'TEST'
        }
        
        response = authenticated_client.post('/api/v1/services/categories', data)
        
        assert response.status_code == 201
        assert response.data['name'] == 'Test Category'
    
    def test_create_service(self, authenticated_client, organization):
        """Test creating service"""
        category = ServiceCategory.objects.create(
            organization=organization,
            name='Therapy',
            code='THR'
        )
        
        data = {
            'organization': organization.id,
            'category': category.id,
            'code': 'THR01',
            'name': 'Test Service',
            'base_price': '10000',
            'unit': 'service',
            'default_duration': 30,
            'vat_rate': '12'
        }
        
        response = authenticated_client.post('/api/v1/services/services', data)
        
        assert response.status_code == 201
        assert response.data['name'] == 'Test Service'
    
    def test_list_services(self, authenticated_client, organization):
        """Test listing services"""
        Service.objects.create(
            organization=organization,
            code='SVC01',
            name='Service 1',
            base_price=5000,
            default_duration=30,
            vat_rate=12
        )
        
        response = authenticated_client.get('/api/v1/services/services')
        
        assert response.status_code == 200
        assert len(response.data['results']) > 0

