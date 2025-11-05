"""
Payments handler
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.inline import get_main_menu_keyboard
from services.api_client import DjangoAPIClient
from services.helpers import format_price
from config import config

router = Router()
api_client = DjangoAPIClient(config.DJANGO_API_URL, config.DJANGO_API_SECRET)


@router.callback_query(F.data == 'menu:payments')
async def show_payments(callback: CallbackQuery, t: callable, telegram_user: any, language: str):
    """Show payments menu"""
    try:
        balance_data = await api_client.get_patient_balance(telegram_user.id)
        balance = balance_data.get('balance', 0)
        
        text = t('payments_balance', balance=format_price(balance))
        
        await callback.message.edit_text(
            text,
            reply_markup=get_main_menu_keyboard(language)
        )
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)

