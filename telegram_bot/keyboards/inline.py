"""
Inline keyboards for Telegram bot
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_keyboard():
    """Language selection keyboard"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='🇷🇺 Русский', callback_data='lang:ru'),
            InlineKeyboardButton(text='🇰🇿 Қазақша', callback_data='lang:kk')
        ]
    ])
    return keyboard


def get_main_menu_keyboard(language='ru'):
    """Main menu keyboard"""
    if language == 'kk':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='📅 Менің жазылымдарым', callback_data='my_appointments')],
            [InlineKeyboardButton(text='🆕 Жазылу', callback_data='book_appointment')],
            [InlineKeyboardButton(text='📄 Құжаттар', callback_data='my_documents')],
            [InlineKeyboardButton(text='🔐 Менің қолжетімділігім', callback_data='my_access')],
            [InlineKeyboardButton(text='👤 Профиль', callback_data='profile')],
            [InlineKeyboardButton(text='💬 Қолдау', callback_data='support')]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='📅 Мои записи', callback_data='my_appointments')],
            [InlineKeyboardButton(text='🆕 Записаться', callback_data='book_appointment')],
            [InlineKeyboardButton(text='📄 Документы', callback_data='my_documents')],
            [InlineKeyboardButton(text='🔐 Мои доступы', callback_data='my_access')],
            [InlineKeyboardButton(text='👤 Профиль', callback_data='profile')],
            [InlineKeyboardButton(text='💬 Поддержка', callback_data='support')]
        ])
    return keyboard


def get_sex_keyboard(language='ru'):
    """Sex selection keyboard"""
    if language == 'kk':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Ер', callback_data='sex:M'),
                InlineKeyboardButton(text='Әйел', callback_data='sex:F')
            ]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Мужской', callback_data='sex:M'),
                InlineKeyboardButton(text='Женский', callback_data='sex:F')
            ]
        ])
    return keyboard


def get_consents_keyboard(language='ru'):
    """Consents agreement keyboard"""
    if language == 'kk':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Келісемін', callback_data='consent:accept')],
            [InlineKeyboardButton(text='❌ Бас тарту', callback_data='consent:decline')]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Принимаю', callback_data='consent:accept')],
            [InlineKeyboardButton(text='❌ Отказаться', callback_data='consent:decline')]
        ])
    return keyboard


def get_access_grants_keyboard(grants):
    """
    Create keyboard for managing access grants
    
    Args:
        grants: List of grant objects
    """
    buttons = []
    for grant in grants[:10]:  # Limit to 10 grants
        grant_id = grant.get('id')
        org_name = grant.get('grantee_org_name', 'Организация')
        is_active = grant.get('is_active', False)
        
        status_icon = '🟢' if is_active else '🔴'
        button_text = f"{status_icon} {org_name}"
        
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f'grant_details:{grant_id}'
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_branches_keyboard(branches):
    """Branches selection keyboard"""
    buttons = []
    for branch in branches[:10]:
        buttons.append([
            InlineKeyboardButton(
                text=branch.get('name', 'Филиал'),
                callback_data=f"branch:{branch.get('id')}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_services_keyboard(services):
    """Services selection keyboard"""
    buttons = []
    for service in services[:10]:
        buttons.append([
            InlineKeyboardButton(
                text=service.get('name', 'Услуга'),
                callback_data=f"service:{service.get('id')}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_doctors_keyboard(doctors):
    """Doctors selection keyboard"""
    buttons = []
    for doctor in doctors[:10]:
        name = doctor.get('full_name', 'Врач')
        buttons.append([
            InlineKeyboardButton(
                text=name,
                callback_data=f"doctor:{doctor.get('id')}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_calendar_keyboard(year, month):
    """Calendar keyboard for date selection"""
    import calendar
    buttons = []
    
    # Month/Year header
    month_name = calendar.month_name[month]
    buttons.append([InlineKeyboardButton(text=f"📅 {month_name} {year}", callback_data="ignore")])
    
    # Weekday headers
    weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    buttons.append([InlineKeyboardButton(text=day, callback_data="ignore") for day in weekdays])
    
    # Calendar days
    cal = calendar.monthcalendar(year, month)
    for week in cal:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton(
                    text=str(day),
                    callback_data=f"date:{year}-{month:02d}-{day:02d}"
                ))
        buttons.append(row)
    
    # Navigation buttons
    buttons.append([
        InlineKeyboardButton(text="◀️", callback_data=f"calendar_prev:{year}:{month}"),
        InlineKeyboardButton(text="▶️", callback_data=f"calendar_next:{year}:{month}")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_slots_keyboard(slots):
    """Time slots selection keyboard"""
    buttons = []
    row = []
    for i, slot in enumerate(slots):
        if slot.get('available'):
            row.append(InlineKeyboardButton(
                text=slot.get('time', '00:00'),
                callback_data=f"time:{slot.get('time')}"
            ))
            if (i + 1) % 3 == 0:
                buttons.append(row)
                row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_confirmation_keyboard(language='ru'):
    """Confirmation keyboard"""
    if language == 'kk':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Растау', callback_data='confirm:yes')],
            [InlineKeyboardButton(text='❌ Болдырмау', callback_data='confirm:no')]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Подтвердить', callback_data='confirm:yes')],
            [InlineKeyboardButton(text='❌ Отменить', callback_data='confirm:no')]
        ])
    return keyboard


def get_appointment_actions_keyboard(appointment_id, language='ru'):
    """Appointment actions keyboard"""
    if language == 'kk':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='📝 Толығырақ', callback_data=f'appointment:{appointment_id}')],
            [InlineKeyboardButton(text='❌ Болдырмау', callback_data=f'cancel_appointment:{appointment_id}')],
            [InlineKeyboardButton(text='⬅️ Артқа', callback_data='back:main')]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='📝 Подробнее', callback_data=f'appointment:{appointment_id}')],
            [InlineKeyboardButton(text='❌ Отменить запись', callback_data=f'cancel_appointment:{appointment_id}')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='back:main')]
        ])
    return keyboard


def get_documents_type_keyboard(language='ru'):
    """Documents type selection keyboard"""
    if language == 'kk':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='📄 Барлық құжаттар', callback_data='docs:all')],
            [InlineKeyboardButton(text='🏥 Нәтижелер', callback_data='docs:results')],
            [InlineKeyboardButton(text='📋 Справки', callback_data='docs:certificates')],
            [InlineKeyboardButton(text='💊 Рецепты', callback_data='docs:prescriptions')],
            [InlineKeyboardButton(text='⬅️ Артқа', callback_data='back:main')]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='📄 Все документы', callback_data='docs:all')],
            [InlineKeyboardButton(text='🏥 Результаты', callback_data='docs:results')],
            [InlineKeyboardButton(text='📋 Справки', callback_data='docs:certificates')],
            [InlineKeyboardButton(text='💊 Рецепты', callback_data='docs:prescriptions')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='back:main')]
        ])
    return keyboard


def get_support_keyboard(language='ru'):
    """Support menu keyboard"""
    if language == 'kk':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='❓ Жиі қойылатын сұрақтар', callback_data='support:faq')],
            [InlineKeyboardButton(text='💬 Оператормен байланысу', callback_data='support:contact')],
            [InlineKeyboardButton(text='⬅️ Артқа', callback_data='back:main')]
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='❓ Часто задаваемые вопросы', callback_data='support:faq')],
            [InlineKeyboardButton(text='💬 Связаться с оператором', callback_data='support:contact')],
            [InlineKeyboardButton(text='⬅️ Назад', callback_data='back:main')]
        ])
    return keyboard


def get_nps_keyboard():
    """NPS rating keyboard (0-10)"""
    buttons = []
    row = []
    for i in range(11):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f'nps:{i}'))
        if (i + 1) % 6 == 0 or i == 10:
            buttons.append(row)
            row = []
    return InlineKeyboardMarkup(inline_keyboard=buttons)