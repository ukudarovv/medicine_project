import logging

logger = logging.getLogger(__name__)


class MockSMSProvider:
    """Mock SMS provider for development"""
    
    def __init__(self, api_key='', api_secret=''):
        self.api_key = api_key
        self.api_secret = api_secret
    
    def send_sms(self, phone, text):
        """Mock send SMS"""
        logger.info(f"[MOCK SMS] To: {phone}, Text: {text}")
        return {
            'success': True,
            'message_id': f'mock_{phone}_{hash(text)}',
            'cost': 15.0  # Mock cost in KZT
        }


def get_sms_provider():
    """Get SMS provider based on settings"""
    from django.conf import settings
    
    provider_type = settings.SMS_PROVIDER
    
    if provider_type == 'mock':
        return MockSMSProvider()
    else:
        return MockSMSProvider()  # Default to mock

