"""
Profile handler
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.inline import get_main_menu_keyboard, get_language_keyboard
from services.api_client import DjangoAPIClient
from config import config

router = Router()
api_client = DjangoAPIClient(config.DJANGO_API_URL, config.DJANGO_API_SECRET)


@router.callback_query(F.data == 'menu:profile')
async def show_profile(callback: CallbackQuery, t: callable, patient: dict, language: str):
    """Show user profile"""
    if not patient:
        await callback.answer(t('not_registered'), show_alert=True)
        return
    
    text = t('profile_data',
        full_name=patient.get('patient_full_name', ''),
        phone=patient.get('patient_phone', ''),
        iin='***',  # Masked
        language=language
    )
    
    await callback.message.edit_text(
        text,
        reply_markup=get_language_keyboard()
    )


@router.callback_query(F.data.startswith('lang:'))
async def change_language(callback: CallbackQuery, t: callable):
    """Change language"""
    language = callback.data.split(':')[1]
    
    # In real implementation, update in database via API
    await callback.answer(t('language_selected'))

