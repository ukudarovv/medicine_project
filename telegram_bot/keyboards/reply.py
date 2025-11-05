"""
Reply keyboards for bot
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_phone_keyboard(language: str = 'ru') -> ReplyKeyboardMarkup:
    """Request phone number keyboard"""
    text = "📱 Телефон нөмірін жіберу" if language == 'kk' else "📱 Отправить номер телефона"
    
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=text, request_contact=True))
    
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_cancel_keyboard(language: str = 'ru') -> ReplyKeyboardMarkup:
    """Cancel operation keyboard"""
    text = "❌ Болдырмау" if language == 'kk' else "❌ Отмена"
    
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=text))
    
    return builder.as_markup(resize_keyboard=True)


def remove_keyboard() -> ReplyKeyboardMarkup:
    """Remove reply keyboard"""
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()

