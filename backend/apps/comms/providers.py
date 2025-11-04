import logging
from typing import Protocol, NamedTuple
from decimal import Decimal
import time

logger = logging.getLogger(__name__)


class SendResult(NamedTuple):
    """Result of SMS send operation"""
    success: bool
    message_id: str
    cost: Decimal
    error: str = ''
    segments: int = 1


class DeliveryStatus(NamedTuple):
    """Delivery status from provider"""
    status: str  # 'sent', 'delivered', 'failed'
    delivered_at: str = ''
    error: str = ''


class SmsProvider(Protocol):
    """SMS Provider interface"""
    
    @property
    def rate_limit_per_min(self) -> int:
        """Rate limit per minute"""
        ...
    
    @property
    def price_per_sms(self) -> Decimal:
        """Price per SMS segment"""
        ...
    
    def send(self, *, sender: str, phone: str, body: str) -> SendResult:
        """Send SMS"""
        ...
    
    def get_status(self, provider_msg_id: str) -> DeliveryStatus:
        """Get delivery status"""
        ...
    
    @staticmethod
    def calculate_segments(text: str, is_cyrillic: bool = True) -> int:
        """Calculate SMS segments"""
        max_chars = 70 if is_cyrillic else 160
        if len(text) <= max_chars:
            return 1
        # For multi-part messages, each segment is slightly smaller
        max_chars_multi = 67 if is_cyrillic else 153
        return (len(text) + max_chars_multi - 1) // max_chars_multi


class MockSMSProvider:
    """Mock SMS provider for development"""
    
    def __init__(self, api_key: str = '', api_secret: str = '', rate_limit: int = 30, price: Decimal = Decimal('15.0')):
        self.api_key = api_key
        self.api_secret = api_secret
        self._rate_limit = rate_limit
        self._price = price
        # Simulate delivery status storage
        self._deliveries = {}
    
    @property
    def rate_limit_per_min(self) -> int:
        return self._rate_limit
    
    @property
    def price_per_sms(self) -> Decimal:
        return self._price
    
    def send(self, *, sender: str, phone: str, body: str) -> SendResult:
        """Mock send SMS with segment calculation"""
        # Detect cyrillic
        is_cyrillic = any('\u0400' <= char <= '\u04FF' for char in body)
        segments = self.calculate_segments(body, is_cyrillic)
        cost = self._price * segments
        
        message_id = f'mock_{int(time.time())}_{hash(phone + body) % 1000000}'
        
        # Simulate delivery (90% success rate)
        import random
        success = random.random() > 0.1
        
        if success:
            # Store for status check
            self._deliveries[message_id] = {
                'status': 'sent',
                'delivered_at': '',
                'phone': phone,
            }
            logger.info(f"[MOCK SMS] Sent to {phone}: {body[:50]}... (segments: {segments}, cost: {cost} KZT)")
            return SendResult(
                success=True,
                message_id=message_id,
                cost=cost,
                segments=segments
            )
        else:
            logger.warning(f"[MOCK SMS] Failed to send to {phone}")
            return SendResult(
                success=False,
                message_id='',
                cost=Decimal('0'),
                error='Mock simulated failure',
                segments=segments
            )
    
    def get_status(self, provider_msg_id: str) -> DeliveryStatus:
        """Mock get delivery status"""
        # Simulate delivery with delay
        delivery = self._deliveries.get(provider_msg_id)
        if not delivery:
            return DeliveryStatus(status='failed', error='Message not found')
        
        # Simulate gradual delivery
        import random
        if delivery['status'] == 'sent' and random.random() > 0.3:
            delivery['status'] = 'delivered'
            delivery['delivered_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
        
        return DeliveryStatus(
            status=delivery['status'],
            delivered_at=delivery.get('delivered_at', ''),
            error=''
        )
    
    @staticmethod
    def calculate_segments(text: str, is_cyrillic: bool = True) -> int:
        """Calculate SMS segments (GSM-7 vs UCS-2)"""
        max_chars = 70 if is_cyrillic else 160
        if len(text) <= max_chars:
            return 1
        # For multi-part messages, each segment is slightly smaller due to UDH
        max_chars_multi = 67 if is_cyrillic else 153
        return (len(text) + max_chars_multi - 1) // max_chars_multi


# ==================== Sprint 4: Kazakhstan SMS Providers ====================


class BeeSMSProvider:
    """
    Beeline Kazakhstan SMS Gateway - Sprint 4
    https://beesms.kz/
    """
    
    def __init__(self, api_key: str, api_secret: str = '', rate_limit: int = 30, price: Decimal = Decimal('18.0')):
        self.api_key = api_key
        self.api_secret = api_secret
        self._rate_limit = rate_limit
        self._price = price
        self.api_url = 'https://beesms.kz/api/v1'
    
    @property
    def rate_limit_per_min(self) -> int:
        return self._rate_limit
    
    @property
    def price_per_sms(self) -> Decimal:
        return self._price
    
    def send(self, *, sender: str, phone: str, body: str) -> SendResult:
        """Send SMS via BeeSMS"""
        import requests
        
        # Detect cyrillic and calculate segments
        is_cyrillic = any('\u0400' <= char <= '\u04FF' for char in body)
        segments = self.calculate_segments(body, is_cyrillic)
        cost = self._price * segments
        
        try:
            response = requests.post(
                f'{self.api_url}/send',
                json={
                    'api_key': self.api_key,
                    'sender': sender,
                    'phone': phone,
                    'message': body,
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"[BeeSMS] Sent to {phone}, ID: {data.get('message_id')}")
                return SendResult(
                    success=True,
                    message_id=str(data.get('message_id', '')),
                    cost=cost,
                    segments=segments
                )
            else:
                logger.error(f"[BeeSMS] Failed: {response.text}")
                return SendResult(
                    success=False,
                    message_id='',
                    cost=Decimal('0'),
                    error=response.text,
                    segments=segments
                )
        except Exception as e:
            logger.error(f"[BeeSMS] Exception: {e}")
            return SendResult(
                success=False,
                message_id='',
                cost=Decimal('0'),
                error=str(e),
                segments=segments
            )
    
    def get_status(self, provider_msg_id: str) -> DeliveryStatus:
        """Get delivery status from BeeSMS"""
        # Mock implementation
        return DeliveryStatus(status='sent')
    
    @staticmethod
    def calculate_segments(text: str, is_cyrillic: bool = True) -> int:
        max_chars = 70 if is_cyrillic else 160
        if len(text) <= max_chars:
            return 1
        max_chars_multi = 67 if is_cyrillic else 153
        return (len(text) + max_chars_multi - 1) // max_chars_multi


class AltelSMSProvider:
    """
    Altel/Tele2 Kazakhstan SMS Gateway - Sprint 4
    """
    
    def __init__(self, api_key: str, api_secret: str = '', rate_limit: int = 30, price: Decimal = Decimal('17.0')):
        self.api_key = api_key
        self.api_secret = api_secret
        self._rate_limit = rate_limit
        self._price = price
        self.api_url = 'https://sms.altel.kz/api'
    
    @property
    def rate_limit_per_min(self) -> int:
        return self._rate_limit
    
    @property
    def price_per_sms(self) -> Decimal:
        return self._price
    
    def send(self, *, sender: str, phone: str, body: str) -> SendResult:
        """Send SMS via Altel"""
        import requests
        
        is_cyrillic = any('\u0400' <= char <= '\u04FF' for char in body)
        segments = self.calculate_segments(body, is_cyrillic)
        cost = self._price * segments
        
        try:
            response = requests.post(
                f'{self.api_url}/send',
                headers={'Authorization': f'Bearer {self.api_key}'},
                json={
                    'from': sender,
                    'to': phone,
                    'text': body,
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"[Altel] Sent to {phone}, ID: {data.get('msg_id')}")
                return SendResult(
                    success=True,
                    message_id=str(data.get('msg_id', '')),
                    cost=cost,
                    segments=segments
                )
            else:
                logger.error(f"[Altel] Failed: {response.text}")
                return SendResult(
                    success=False,
                    message_id='',
                    cost=Decimal('0'),
                    error=response.text,
                    segments=segments
                )
        except Exception as e:
            logger.error(f"[Altel] Exception: {e}")
            return SendResult(
                success=False,
                message_id='',
                cost=Decimal('0'),
                error=str(e),
                segments=segments
            )
    
    def get_status(self, provider_msg_id: str) -> DeliveryStatus:
        """Get delivery status from Altel"""
        return DeliveryStatus(status='sent')
    
    @staticmethod
    def calculate_segments(text: str, is_cyrillic: bool = True) -> int:
        max_chars = 70 if is_cyrillic else 160
        if len(text) <= max_chars:
            return 1
        max_chars_multi = 67 if is_cyrillic else 153
        return (len(text) + max_chars_multi - 1) // max_chars_multi


def get_sms_provider(organization=None) -> MockSMSProvider:
    """Get SMS provider based on settings or organization config"""
    from django.conf import settings
    
    # If organization has custom provider, use it
    if organization:
        from .models import SmsProvider as SmsProviderModel
        try:
            provider_config = SmsProviderModel.objects.filter(
                organization=organization,
                is_active=True
            ).first()
            if provider_config:
                # Check provider name to determine which class to use
                provider_name = provider_config.name.lower()
                
                if 'beeline' in provider_name or 'beesms' in provider_name:
                    return BeeSMSProvider(
                        api_key=provider_config.api_key,
                        api_secret=provider_config.api_secret,
                        rate_limit=provider_config.rate_limit_per_min,
                        price=provider_config.price_per_sms
                    )
                elif 'altel' in provider_name or 'tele2' in provider_name:
                    return AltelSMSProvider(
                        api_key=provider_config.api_key,
                        api_secret=provider_config.api_secret,
                        rate_limit=provider_config.rate_limit_per_min,
                        price=provider_config.price_per_sms
                    )
                else:
                    return MockSMSProvider(
                        api_key=provider_config.api_key,
                        api_secret=provider_config.api_secret,
                        rate_limit=provider_config.rate_limit_per_min,
                        price=provider_config.price_per_sms
                    )
        except Exception as e:
            logger.warning(f"Failed to load provider config: {e}")
    
    # Default to mock provider
    provider_type = getattr(settings, 'SMS_PROVIDER', 'mock')
    
    if provider_type == 'mock':
        return MockSMSProvider()
    elif provider_type == 'beesms':
        return BeeSMSProvider(api_key=getattr(settings, 'SMS_API_KEY', ''))
    elif provider_type == 'altel':
        return AltelSMSProvider(api_key=getattr(settings, 'SMS_API_KEY', ''))
    else:
        logger.warning(f"Unknown provider type '{provider_type}', falling back to mock")
        return MockSMSProvider()

