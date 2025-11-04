"""
Kaspi QR Payment Integration (Kazakhstan) - Sprint 4
"""
import requests
import hashlib
import json
from django.conf import settings


class KaspiQRService:
    """
    Kaspi QR payment integration service
    Documentation: https://kaspi.kz/merchantapi/
    """
    
    def __init__(self, merchant_id, api_key, test_mode=True):
        self.merchant_id = merchant_id
        self.api_key = api_key
        self.test_mode = test_mode
        self.base_url = 'https://kaspi.kz/merchantapi' if not test_mode else 'https://test.kaspi.kz/merchantapi'
    
    def generate_qr(self, invoice_id, amount, description=''):
        """
        Generate Kaspi QR code for payment
        
        Args:
            invoice_id: Invoice ID in your system
            amount: Amount in KZT
            description: Payment description
        
        Returns:
            dict with qr_code_url and payment_id
        """
        # In test mode, return mock data
        if self.test_mode:
            return {
                'success': True,
                'qr_code_url': f'https://test.kaspi.kz/qr/{invoice_id}',
                'payment_id': f'KASPI_TEST_{invoice_id}',
                'amount': float(amount),
                'status': 'pending'
            }
        
        # Real implementation would be here
        # This is a simplified mock implementation
        payload = {
            'merchant_id': self.merchant_id,
            'order_id': str(invoice_id),
            'amount': float(amount),
            'currency': 'KZT',
            'description': description,
        }
        
        # Add signature
        signature = self._generate_signature(payload)
        payload['signature'] = signature
        
        try:
            response = requests.post(
                f'{self.base_url}/qr/create',
                json=payload,
                headers={'Authorization': f'Bearer {self.api_key}'},
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
        """
        Check payment status
        
        Returns:
            dict with status (pending|completed|failed)
        """
        if self.test_mode:
            return {
                'payment_id': payment_id,
                'status': 'pending',
                'amount': 0,
            }
        
        try:
            response = requests.get(
                f'{self.base_url}/payment/status/{payment_id}',
                headers={'Authorization': f'Bearer {self.api_key}'},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_signature(self, payload):
        """Generate request signature"""
        # Sort payload keys
        sorted_data = sorted(payload.items())
        data_string = '&'.join([f'{k}={v}' for k, v in sorted_data])
        
        # Add secret key
        data_string += self.api_key
        
        # Generate SHA256 hash
        signature = hashlib.sha256(data_string.encode()).hexdigest()
        return signature


def get_kaspi_service(organization):
    """
    Get configured Kaspi service for organization
    """
    from apps.billing.models import PaymentProvider
    
    try:
        provider = PaymentProvider.objects.get(
            organization=organization,
            provider_type='kaspi',
            is_active=True
        )
        return KaspiQRService(
            merchant_id=provider.merchant_id,
            api_key=provider.api_key,
            test_mode=provider.is_test_mode
        )
    except PaymentProvider.DoesNotExist:
        return None

