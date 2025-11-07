"""
Internationalization middleware
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Update, User
import json
import os


class I18nMiddleware(BaseMiddleware):
    """
    Middleware for handling multiple languages (RU/KK)
    """
    
    def __init__(self):
        super().__init__()
        self.translations = self.load_translations()
    
    def load_translations(self) -> Dict[str, Dict]:
        """Load translation files"""
        translations = {}
        locales_dir = os.path.join(os.path.dirname(__file__), '..', 'locales')
        
        for lang in ['ru', 'kk']:
            file_path = os.path.join(locales_dir, f'{lang}.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    translations[lang] = json.load(f)
            else:
                translations[lang] = {}
        
        return translations
    
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        """Process update with i18n"""
        
        # Get user's language from database or default to 'ru'
        user_language = data.get('user_language', 'ru')
        
        # For unregistered users in registration flow, check FSM state for language
        if not data.get('is_registered', False):
            state = data.get('state')
            if state:
                try:
                    state_data = await state.get_data()
                    if 'language' in state_data:
                        user_language = state_data['language']
                except Exception:
                    pass
        
        # Add translation function to data
        def t(key: str, **kwargs) -> str:
            """Translate key with optional formatting"""
            text = self.translations.get(user_language, {}).get(key, key)
            if kwargs:
                return text.format(**kwargs)
            return text
        
        data['t'] = t
        data['language'] = user_language
        
        return await handler(event, data)

