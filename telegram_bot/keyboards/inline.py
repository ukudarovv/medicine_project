"""
Inline keyboards for bot
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict
from datetime import date, datetime, timedelta


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇰🇿 Қазақ", callback_data="lang:kk")
    )
    return builder.as_markup()


def get_main_menu_keyboard(language: str = 'ru') -> InlineKeyboardMarkup:
    """Main menu keyboard"""
    if language == 'kk':
        buttons = [
            ("📅 Жазылу", "menu:booking"),
            ("📋 Менің жазулартым", "menu:my_appointments"),
            ("📄 Құжаттар", "menu:documents"),
            ("💳 Төлемдер", "menu:payments"),
            ("👤 Профиль", "menu:profile"),
            ("❓ Көмек", "menu:support"),
        ]
    else:
        buttons = [
            ("📅 Записаться", "menu:booking"),
            ("📋 Мои записи", "menu:my_appointments"),
            ("📄 Документы", "menu:documents"),
            ("💳 Оплата", "menu:payments"),
            ("👤 Профиль", "menu:profile"),
            ("❓ Поддержка", "menu:support"),
        ]
    
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    return builder.as_markup()


def get_sex_keyboard(language: str = 'ru') -> InlineKeyboardMarkup:
    """Sex selection keyboard"""
    if language == 'kk':
        buttons = [
            ("👨 Ер", "sex:M"),
            ("👩 Әйел", "sex:F")
        ]
    else:
        buttons = [
            ("👨 Мужской", "sex:M"),
            ("👩 Женский", "sex:F")
        ]
    
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    return builder.as_markup()


def get_consents_keyboard(language: str = 'ru') -> InlineKeyboardMarkup:
    """Consents keyboard"""
    if language == 'kk':
        text = "✅ Келісемін"
    else:
        text = "✅ Согласен"
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, callback_data="consent:accept"))
    
    return builder.as_markup()


def get_branches_keyboard(branches: List[Dict]) -> InlineKeyboardMarkup:
    """Branches selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    for branch in branches:
        builder.row(
            InlineKeyboardButton(
                text=branch['name'],
                callback_data=f"branch:{branch['id']}"
            )
        )
    
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="back:main"))
    
    return builder.as_markup()


def get_services_keyboard(services: List[Dict]) -> InlineKeyboardMarkup:
    """Services selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    for service in services:
        price = f"{service['price']} ₸" if service.get('price') else ""
        text = f"{service['name']} {price}".strip()
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"service:{service['id']}"
            )
        )
    
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="back:branch"))
    
    return builder.as_markup()


def get_doctors_keyboard(doctors: List[Dict]) -> InlineKeyboardMarkup:
    """Doctors selection keyboard"""
    builder = InlineKeyboardBuilder()
    
    for doctor in doctors:
        specialty = doctor.get('specialty', '')
        text = f"{doctor['full_name']}"
        if specialty:
            text += f" ({specialty})"
        
        builder.row(
            InlineKeyboardButton(
                text=text,
                callback_data=f"doctor:{doctor['id']}"
            )
        )
    
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="back:service"))
    
    return builder.as_markup()


def get_calendar_keyboard(year: int, month: int) -> InlineKeyboardMarkup:
    """Calendar keyboard for date selection"""
    builder = InlineKeyboardBuilder()
    
    # Month and year header
    months = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }
    
    builder.row(
        InlineKeyboardButton(text="◀", callback_data=f"cal:prev:{year}:{month}"),
        InlineKeyboardButton(text=f"{months[month]} {year}", callback_data="ignore"),
        InlineKeyboardButton(text="▶", callback_data=f"cal:next:{year}:{month}")
    )
    
    # Weekday headers
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    buttons = [InlineKeyboardButton(text=day, callback_data="ignore") for day in weekdays]
    builder.row(*buttons)
    
    # Calendar days
    import calendar
    cal = calendar.monthcalendar(year, month)
    today = date.today()
    
    for week in cal:
        buttons = []
        for day in week:
            if day == 0:
                buttons.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                current_date = date(year, month, day)
                if current_date < today:
                    # Past date - disabled
                    buttons.append(InlineKeyboardButton(text=str(day), callback_data="ignore"))
                else:
                    # Future date - clickable
                    buttons.append(InlineKeyboardButton(
                        text=str(day),
                        callback_data=f"date:{year}-{month:02d}-{day:02d}"
                    ))
        builder.row(*buttons)
    
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="back:doctor"))
    
    return builder.as_markup()


def get_time_slots_keyboard(slots: List[Dict]) -> InlineKeyboardMarkup:
    """Time slots keyboard"""
    builder = InlineKeyboardBuilder()
    
    available_slots = [s for s in slots if s['available']]
    
    if not available_slots:
        builder.row(InlineKeyboardButton(text="Нет свободных слотов", callback_data="ignore"))
    else:
        # Show in rows of 3
        row_buttons = []
        for slot in available_slots:
            row_buttons.append(
                InlineKeyboardButton(
                    text=slot['time'],
                    callback_data=f"time:{slot['time']}"
                )
            )
            
            if len(row_buttons) == 3:
                builder.row(*row_buttons)
                row_buttons = []
        
        if row_buttons:
            builder.row(*row_buttons)
    
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="back:date"))
    
    return builder.as_markup()


def get_confirmation_keyboard(language: str = 'ru') -> InlineKeyboardMarkup:
    """Booking confirmation keyboard"""
    if language == 'kk':
        buttons = [
            ("✅ Растау", "confirm:yes"),
            ("❌ Болдырмау", "confirm:no")
        ]
    else:
        buttons = [
            ("✅ Подтвердить", "confirm:yes"),
            ("❌ Отменить", "confirm:no")
        ]
    
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    return builder.as_markup()


def get_appointment_actions_keyboard(appointment_id: int, language: str = 'ru') -> InlineKeyboardMarkup:
    """Actions for specific appointment"""
    if language == 'kk':
        buttons = [
            ("📍 Картада көрсету", f"apt:map:{appointment_id}"),
            ("🔄 Басқа уақытқа ауыстыру", f"apt:reschedule:{appointment_id}"),
            ("❌ Болдырмау", f"apt:cancel:{appointment_id}"),
        ]
    else:
        buttons = [
            ("📍 Показать на карте", f"apt:map:{appointment_id}"),
            ("🔄 Перенести", f"apt:reschedule:{appointment_id}"),
            ("❌ Отменить", f"apt:cancel:{appointment_id}"),
        ]
    
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="back:my_appointments"))
    
    return builder.as_markup()


def get_documents_type_keyboard(language: str = 'ru') -> InlineKeyboardMarkup:
    """Document types keyboard"""
    if language == 'kk':
        buttons = [
            ("📋 Бағыттамалар", "doc:direction"),
            ("💊 Рецепттер", "doc:recipe"),
            ("📊 Зерттеу нәтижелері", "doc:result"),
            ("📄 Салық шегерімі үшін анықтама", "doc:tax"),
        ]
    else:
        buttons = [
            ("📋 Направления", "doc:direction"),
            ("💊 Рецепты", "doc:recipe"),
            ("📊 Результаты исследований", "doc:result"),
            ("📄 Справка для налогового вычета", "doc:tax"),
        ]
    
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="back:main"))
    
    return builder.as_markup()


def get_nps_keyboard() -> InlineKeyboardMarkup:
    """NPS score keyboard (0-10)"""
    builder = InlineKeyboardBuilder()
    
    # First row: 0-5
    row1 = [InlineKeyboardButton(text=str(i), callback_data=f"nps:{i}") for i in range(6)]
    builder.row(*row1)
    
    # Second row: 6-10
    row2 = [InlineKeyboardButton(text=str(i), callback_data=f"nps:{i}") for i in range(6, 11)]
    builder.row(*row2)
    
    return builder.as_markup()


def get_support_keyboard(language: str = 'ru') -> InlineKeyboardMarkup:
    """Support menu keyboard"""
    if language == 'kk':
        buttons = [
            ("❓ Жиі қойылатын сұрақтар", "support:faq"),
            ("💬 Оператормен байланысу", "support:contact"),
            ("📍 Мекенжай және байланыс", "support:address"),
            ("💰 Баға парағы", "support:price"),
            ("🕐 Жұмыс кестесі", "support:schedule"),
        ]
    else:
        buttons = [
            ("❓ Часто задаваемые вопросы", "support:faq"),
            ("💬 Связаться с оператором", "support:contact"),
            ("📍 Адрес и контакты", "support:address"),
            ("💰 Прайс-лист", "support:price"),
            ("🕐 График работы", "support:schedule"),
        ]
    
    builder = InlineKeyboardBuilder()
    for text, callback_data in buttons:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback_data))
    
    builder.row(InlineKeyboardButton(text="« Назад", callback_data="back:main"))
    
    return builder.as_markup()


def get_back_to_main_keyboard(language: str = 'ru') -> InlineKeyboardMarkup:
    """Simple back to main menu button"""
    text = "« Басты мәзірге" if language == 'kk' else "« Главное меню"
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=text, callback_data="back:main"))
    return builder.as_markup()

