"""
Support handler
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.inline import get_support_keyboard, get_main_menu_keyboard
from services.api_client import DjangoAPIClient
from config import config

router = Router()
api_client = DjangoAPIClient(config.DJANGO_API_URL, config.DJANGO_API_SECRET)


@router.callback_query(F.data == 'menu:support')
async def show_support_menu(callback: CallbackQuery, t: callable, language: str):
    """Show support menu"""
    await callback.message.edit_text(
        t('support_menu'),
        reply_markup=get_support_keyboard(language)
    )


@router.callback_query(F.data == 'support:faq')
async def show_faq(callback: CallbackQuery, t: callable):
    """Show FAQ"""
    try:
        faqs = await api_client.get_faq()
        
        text = t('support_faq') + '\n\n'
        for faq in faqs:
            text += f"❓ {faq['question']}\n💬 {faq['answer']}\n\n"
        
        await callback.message.edit_text(text)
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data == 'support:contact')
async def contact_operator(callback: CallbackQuery, t: callable, telegram_user: any):
    """Create support ticket"""
    try:
        await api_client.create_support_ticket(
            telegram_user.id,
            "Запрос из бота",
            "Пользователь хочет связаться с оператором"
        )
        
        await callback.answer(t('support_ticket_created'), show_alert=True)
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)

