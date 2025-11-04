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
    else:
        # Future: add real provider implementations (Smsc.kz, etc.)
        logger.warning(f"Unknown provider type '{provider_type}', falling back to mock")
        return MockSMSProvider()

