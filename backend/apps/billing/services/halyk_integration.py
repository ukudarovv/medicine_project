"""
Halyk Pay Integration (Kazakhstan) - Sprint 4
"""
import requests
import hashlib
import base64
from django.conf import settings


class HalykPayService:
    """
    Halyk Pay payment integration service
    """
    
    def __init__(self, merchant_id, api_key, api_secret, test_mode=True):
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.test_mode = test_mode
        self.base_url = 'https://test-epay.homebank.kz' if test_mode else 'https://epay.homebank.kz'
    
    def initiate_payment(self, invoice_id, amount, description='', return_url=''):
        """
        Initiate Halyk Pay payment
        
        Args:
            invoice_id: Invoice ID in your system
            amount: Amount in KZT
            description: Payment description
            return_url: URL to return after payment
        
        Returns:
            dict with redirect_url for payment page
        """
        # In test mode, return mock data
        if self.test_mode:
            return {
                'success': True,
                'payment_id': f'HALYK_TEST_{invoice_id}',
                'redirect_url': f'https://test-epay.homebank.kz/payment/{invoice_id}',
                'amount': float(amount)
            }
        
        # Real implementation
        payload = {
            'merchant': self.merchant_id,
            'order_id': str(invoice_id),
            'amount': float(amount),
            'currency': 'KZT',
            'description': description,
            'return_url': return_url or settings.SITE_URL + '/billing/payment-success/',
            'failure_url': settings.SITE_URL + '/billing/payment-failure/',
        }
        
        # Generate signature
        signature = self._generate_signature(payload)
        payload['signature'] = signature
        
        try:
            response = requests.post(
                f'{self.base_url}/payment/create',
                json=payload,
                auth=(self.api_key, self.api_secret),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def check_payment_status(self, payment_id):
        """Check payment status"""
        if self.test_mode:
            return {
                'payment_id': payment_id,
                'status': 'pending'
            }
        
        try:
            response = requests.get(
                f'{self.base_url}/payment/status',
                params={'payment_id': payment_id},
                auth=(self.api_key, self.api_secret),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_callback(self, callback_data, signature):
        """Verify webhook signature"""
        expected_signature = self._generate_signature(callback_data)
        return signature == expected_signature
    
    def _generate_signature(self, payload):
        """Generate request signature"""
        # Sort by keys
        sorted_items = sorted(payload.items())
        data_string = ';'.join([f'{k}={v}' for k, v in sorted_items])
        data_string += ';' + self.api_secret
        
        # Generate base64-encoded hash
        signature = hashlib.sha512(data_string.encode()).digest()
        return base64.b64encode(signature).decode()


def get_halyk_service(organization):
    """
    Get configured Halyk service for organization
    """
    from apps.billing.models import PaymentProvider
    
    try:
        provider = PaymentProvider.objects.get(
            organization=organization,
            provider_type='halyk',
            is_active=True
        )
        return HalykPayService(
            merchant_id=provider.merchant_id,
            api_key=provider.api_key,
            api_secret=provider.api_secret,
            test_mode=provider.is_test_mode
        )
    except PaymentProvider.DoesNotExist:
        return None

