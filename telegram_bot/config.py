"""
Bot configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Bot configuration"""
    
    # Telegram Bot
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    WEBHOOK_URL = os.getenv('TELEGRAM_WEBHOOK_URL', '')
    WEBHOOK_PATH = '/webhook'
    WEBHOOK_SECRET = os.getenv('TELEGRAM_WEBHOOK_SECRET', 'change-this-secret')
    
    # Django API
    DJANGO_API_URL = os.getenv('DJANGO_API_URL', 'http://backend:8000')
    DJANGO_API_SECRET = os.getenv('TELEGRAM_BOT_API_SECRET', 'change-this-secret-in-production')
    
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '1'))
    
    # Bot settings
    USE_WEBHOOK = os.getenv('USE_WEBHOOK', 'false').lower() == 'true'
    WEBAPP_HOST = os.getenv('WEBAPP_HOST', '0.0.0.0')
    WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', '8080'))
    
    # Organization (for testing)
    DEFAULT_ORGANIZATION_ID = int(os.getenv('DEFAULT_ORGANIZATION_ID', '1'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError('TELEGRAM_BOT_TOKEN is required')
        if not cls.DJANGO_API_SECRET:
            raise ValueError('TELEGRAM_BOT_API_SECRET is required')
        return True


config = Config()

