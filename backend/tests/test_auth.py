import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_login_success(self, api_client, admin_user):
        """Test successful login"""
        response = api_client.post('/api/v1/auth/login', {
            'username': 'admin',
            'password': 'testpass123'
        })
        
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data
    
    def test_login_invalid_credentials(self, api_client, admin_user):
        """Test login with invalid credentials"""
        response = api_client.post('/api/v1/auth/login', {
            'username': 'admin',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 400
    
    def test_me_endpoint(self, authenticated_client, admin_user):
        """Test /me endpoint"""
        response = authenticated_client.get('/api/v1/auth/me')
        
        assert response.status_code == 200
        assert response.data['username'] == 'admin'
        assert response.data['role'] == 'owner'
    
    def test_me_unauthorized(self, api_client):
        """Test /me endpoint without auth"""
        response = api_client.get('/api/v1/auth/me')
        
        assert response.status_code == 401


@pytest.mark.django_db
class TestUserModel:
    """Test User model"""
    
    def test_create_user(self, organization):
        """Test creating user"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@test.com',
            organization=organization
        )
        
        assert user.username == 'testuser'
        assert user.check_password('testpass123')
        assert user.organization == organization
    
    def test_user_roles(self, organization):
        """Test user roles"""
        user = User.objects.create_user(
            username='doctor',
            password='test',
            role='doctor',
            organization=organization
        )
        
        assert user.role == 'doctor'

