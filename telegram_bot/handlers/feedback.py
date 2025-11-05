"""
Feedback handler
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.inline import get_nps_keyboard
from services.api_client import DjangoAPIClient
from config import config

router = Router()
api_client = DjangoAPIClient(config.DJANGO_API_URL, config.DJANGO_API_SECRET)


@router.callback_query(F.data.startswith('feedback:'))
async def request_feedback(callback: CallbackQuery, t: callable):
    """Request NPS feedback"""
    appointment_id = int(callback.data.split(':')[1])
    
    await callback.message.edit_text(
        t('feedback_score'),
        reply_markup=get_nps_keyboard()
    )


@router.callback_query(F.data.startswith('nps:'))
async def save_feedback(callback: CallbackQuery, t: callable, telegram_user: any):
    """Save NPS score"""
    score = int(callback.data.split(':')[1])
    
    # In real implementation, get appointment_id from state
    appointment_id = 1  # Mock
    
    try:
        result = await api_client.create_feedback(
            telegram_user.id,
            appointment_id,
            score
        )
        
        if score <= 6:
            await callback.message.edit_text(t('feedback_low_score_alert'))
        else:
            await callback.message.edit_text(t('feedback_thanks'))
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)

