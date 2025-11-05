"""
My appointments handler
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.inline import get_appointment_actions_keyboard, get_main_menu_keyboard
from services.api_client import DjangoAPIClient
from config import config

router = Router()
api_client = DjangoAPIClient(config.DJANGO_API_URL, config.DJANGO_API_SECRET)


@router.callback_query(F.data == 'menu:my_appointments')
async def show_my_appointments(callback: CallbackQuery, t: callable, telegram_user: any, language: str):
    """Show user's appointments"""
    try:
        appointments = await api_client.get_my_appointments(telegram_user.id)
        
        if not appointments:
            await callback.message.edit_text(
                t('my_appointments_empty'),
                reply_markup=get_main_menu_keyboard(language)
            )
            return
        
        text = t('my_appointments_list') + '\n\n'
        for apt in appointments[:5]:  # Show last 5
            text += f"📅 {apt['date']} {apt['time_from']} - {apt['doctor_name']}\n"
        
        await callback.message.edit_text(text)
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data.startswith('apt:cancel:'))
async def cancel_appointment(callback: CallbackQuery, t: callable):
    """Cancel appointment"""
    apt_id = int(callback.data.split(':')[2])
    
    try:
        await api_client.cancel_appointment(apt_id)
        await callback.answer(t('appointment_cancelled'))
        await callback.message.edit_text(t('appointment_cancelled'))
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)

