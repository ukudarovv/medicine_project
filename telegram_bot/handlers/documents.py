"""
Documents handler
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.inline import get_documents_type_keyboard, get_main_menu_keyboard
from services.api_client import DjangoAPIClient
from config import config

router = Router()
api_client = DjangoAPIClient(config.DJANGO_API_URL, config.DJANGO_API_SECRET)


@router.callback_query(F.data == 'menu:documents')
async def show_documents_menu(callback: CallbackQuery, t: callable, language: str):
    """Show documents menu"""
    await callback.message.edit_text(
        t('documents_choose_type'),
        reply_markup=get_documents_type_keyboard(language)
    )


@router.callback_query(F.data.startswith('doc:'))
async def show_documents_list(callback: CallbackQuery, t: callable, telegram_user: any):
    """Show documents of specific type"""
    doc_type = callback.data.split(':')[1]
    
    try:
        documents = await api_client.get_documents(telegram_user.id, doc_type)
        
        if not documents:
            await callback.answer(t('documents_empty'), show_alert=True)
            return
        
        text = t('documents_list') + '\n\n'
        for doc in documents:
            text += f"📄 {doc['title']} - {doc['created_at'][:10]}\n"
        
        await callback.message.edit_text(text)
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)

