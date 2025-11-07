"""
Start and registration handler
"""
from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from states.registration import RegistrationStates
from keyboards.inline import get_language_keyboard, get_main_menu_keyboard, get_sex_keyboard, get_consents_keyboard
from keyboards.reply import get_phone_keyboard, remove_keyboard
from services.api_client import DjangoAPIClient
from services.helpers import validate_phone
from config import config

logger = logging.getLogger(__name__)

router = Router()
api_client = DjangoAPIClient(config.DJANGO_API_URL, config.DJANGO_API_SECRET)


@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext, is_registered: bool, t: callable):
    """Handle /start command"""
    if is_registered:
        # Already registered - show main menu
        await message.answer(
            t('start_welcome'),
            reply_markup=get_main_menu_keyboard()
        )
    else:
        # Not registered - start registration
        await message.answer(
            t('start_welcome') + '\n\n' + t('start_choose_language'),
            reply_markup=get_language_keyboard()
        )
        await state.set_state(RegistrationStates.language)


@router.callback_query(F.data.startswith('lang:'), StateFilter(RegistrationStates.language, None))
async def select_language(callback: CallbackQuery, state: FSMContext, t: callable):
    """Select language"""
    language = callback.data.split(':')[1]
    
    await state.update_data(language=language)
    await callback.answer(t('language_selected'))
    
    # Start registration
    await callback.message.edit_text(t('reg_first_name'))
    await state.set_state(RegistrationStates.first_name)


@router.message(RegistrationStates.first_name)
async def get_first_name(message: Message, state: FSMContext, t: callable):
    """Get first name"""
    await state.update_data(first_name=message.text)
    await message.answer(t('reg_last_name'))
    await state.set_state(RegistrationStates.last_name)


@router.message(RegistrationStates.last_name)
async def get_last_name(message: Message, state: FSMContext, t: callable):
    """Get last name"""
    await state.update_data(last_name=message.text)
    await message.answer(t('reg_middle_name'))
    await state.set_state(RegistrationStates.middle_name)


@router.message(RegistrationStates.middle_name)
async def get_middle_name(message: Message, state: FSMContext, t: callable):
    """Get middle name"""
    if message.text == '/skip':
        middle_name = ''
    else:
        middle_name = message.text
    
    await state.update_data(middle_name=middle_name)
    
    # Get language from state
    data = await state.get_data()
    user_language = data.get('language', 'ru')
    
    await message.answer(
        t('reg_phone'),
        reply_markup=get_phone_keyboard(user_language)
    )
    await state.set_state(RegistrationStates.phone)


@router.message(RegistrationStates.phone, F.content_type == 'contact')
async def get_phone_contact(message: Message, state: FSMContext, t: callable):
    """Get phone from contact"""
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    
    await message.answer(
        t('reg_birth_date'),
        reply_markup=remove_keyboard()
    )
    await state.set_state(RegistrationStates.birth_date)


@router.message(RegistrationStates.phone)
async def get_phone_text(message: Message, state: FSMContext, t: callable):
    """Get phone as text"""
    try:
        phone = validate_phone(message.text)
        await state.update_data(phone=phone)
        
        await message.answer(t('reg_birth_date'))
        await state.set_state(RegistrationStates.birth_date)
    except ValueError:
        await message.answer(t('error_general'))


@router.message(RegistrationStates.birth_date)
async def get_birth_date(message: Message, state: FSMContext, t: callable):
    """Get birth date"""
    try:
        # Parse DD.MM.YYYY
        birth_date = datetime.strptime(message.text, '%d.%m.%Y').date()
        
        # Check if date is not in the future
        from datetime import date
        if birth_date > date.today():
            await message.answer(t('reg_birth_date_invalid'))
            return
        
        await state.update_data(birth_date=birth_date.isoformat())
        
        # Get language from state
        data = await state.get_data()
        user_language = data.get('language', 'ru')
        
        await message.answer(
            t('reg_sex'),
            reply_markup=get_sex_keyboard(user_language)
        )
        await state.set_state(RegistrationStates.sex)
    except ValueError:
        await message.answer(t('reg_birth_date_invalid'))


@router.callback_query(F.data.startswith('sex:'), StateFilter(RegistrationStates.sex))
async def select_sex(callback: CallbackQuery, state: FSMContext, t: callable):
    """Select sex"""
    sex = callback.data.split(':')[1]
    await state.update_data(sex=sex)
    
    await callback.message.edit_text(t('reg_iin'))
    await state.set_state(RegistrationStates.iin)


@router.message(RegistrationStates.iin)
async def get_iin(message: Message, state: FSMContext, t: callable):
    """Get IIN"""
    iin = message.text.replace(' ', '').replace('-', '')
    
    # Basic validation: must be exactly 12 digits
    if not iin.isdigit() or len(iin) != 12:
        await message.answer(t('reg_iin_invalid'))
        return
    
    # Save IIN
    await state.update_data(iin=iin)
    
    # Try to verify IIN via API (optional - continue if API unavailable)
    iin_verified = False
    try:
        result = await api_client.verify_iin(iin)
        if result.get('valid'):
            iin_verified = True
        else:
            # IIN is invalid according to API
            error_msg = result.get('error')
            if error_msg:
                await message.answer(f"{t('reg_iin_invalid')}\n\n{error_msg}")
            else:
                await message.answer(t('reg_iin_invalid'))
            return
    except Exception as e:
        # API unavailable - log error but continue registration
        logger.warning(f"IIN verification API unavailable: {e}. Continuing without verification.")
        iin_verified = False
    
    # Get language from state (not from middleware, as user is not registered yet)
    data = await state.get_data()
    user_language = data.get('language', 'ru')
    
    # Continue to consents
    await message.answer(
        t('reg_consents'),
        reply_markup=get_consents_keyboard(user_language)
    )
    await state.set_state(RegistrationStates.consents)


@router.callback_query(F.data == 'consent:accept', StateFilter(RegistrationStates.consents))
async def accept_consents(callback: CallbackQuery, state: FSMContext, t: callable, telegram_user: any):
    """Accept consents and complete registration"""
    data = await state.get_data()
    
    # Prepare data for API
    patient_data = {
        'telegram_user_id': telegram_user.id,
        'telegram_username': telegram_user.username or '',
        'language': data.get('language', 'ru'),
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'middle_name': data.get('middle_name', ''),
        'phone': data['phone'],
        'birth_date': data['birth_date'],
        'sex': data['sex'],
        'iin': data.get('iin', ''),
        'consents': {
            'personal_data': True,
            'medical_intervention': True,
            'marketing': True
        },
        'organization_id': config.DEFAULT_ORGANIZATION_ID
    }
    
    logger.info(f"Registering patient via API: {patient_data['first_name']} {patient_data['last_name']}")
    logger.debug(f"Patient data: {patient_data}")
    
    try:
        result = await api_client.upsert_patient(patient_data)
        logger.info(f"Patient registered successfully: {result}")
        
        await callback.message.edit_text(
            t('reg_complete', name=data['first_name'])
        )
        
        await callback.message.answer(
            t('main_menu'),
            reply_markup=get_main_menu_keyboard(data.get('language', 'ru'))
        )
        
        await state.clear()
    except Exception as e:
        logger.error(f"Error completing registration: {e}", exc_info=True)
        await callback.message.edit_text(t('error_general'))


@router.callback_query(F.data == 'consent:decline', StateFilter(RegistrationStates.consents))
async def decline_consents(callback: CallbackQuery, state: FSMContext, t: callable):
    """Decline consents and cancel registration"""
    await state.clear()
    await callback.message.edit_text(t('reg_declined'))


@router.callback_query(F.data == 'back:main')
async def back_to_main(callback: CallbackQuery, language: str):
    """Back to main menu"""
    await callback.message.edit_text(
        callback.message.text,
        reply_markup=get_main_menu_keyboard(language)
    )


@router.callback_query(F.data == 'my_access')
async def callback_my_access(callback: CallbackQuery, t: callable, telegram_user: any):
    """Handle my_access callback from main menu"""
    from handlers.consent import cmd_my_access
    await cmd_my_access(callback.message, t, telegram_user)
    await callback.answer()
