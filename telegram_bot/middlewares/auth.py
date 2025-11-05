"""
Authentication middleware
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update
from services.api_client import DjangoAPIClient
from config import config


class AuthMiddleware(BaseMiddleware):
    """
    Middleware to check if user is registered and load their data
    """
    
    def __init__(self):
        super().__init__()
        self.api_client = DjangoAPIClient(
            base_url=config.DJANGO_API_URL,
            api_token=config.DJANGO_API_SECRET
        )
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """Check user authentication"""
        
        # Get user from update
        user = None
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user
        
        if not user:
            return await handler(event, data)
        
        # Try to get patient data from API
        try:
            patient_data = await self.api_client.get_patient_by_telegram(user.id)
            data['is_registered'] = True
            data['patient'] = patient_data
            data['user_language'] = patient_data.get('language', 'ru')
        except Exception:
            data['is_registered'] = False
            data['patient'] = None
            data['user_language'] = 'ru'
        
        data['telegram_user'] = user
        
        return await handler(event, data)

