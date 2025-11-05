"""
Booking appointments handler
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, date

from states.booking import BookingStates
from keyboards.inline import (
    get_branches_keyboard, get_services_keyboard, get_doctors_keyboard,
    get_calendar_keyboard, get_time_slots_keyboard, get_confirmation_keyboard,
    get_main_menu_keyboard
)
from services.api_client import DjangoAPIClient
from services.helpers import format_date, format_price, generate_ics_file
from config import config

router = Router()
api_client = DjangoAPIClient(config.DJANGO_API_URL, config.DJANGO_API_SECRET)


@router.callback_query(F.data == 'menu:booking')
async def start_booking(callback: CallbackQuery, state: FSMContext, t: callable, is_registered: bool):
    """Start booking process"""
    if not is_registered:
        await callback.answer(t('not_registered'), show_alert=True)
        return
    
    # Get branches
    try:
        branches = await api_client.get_branches(config.DEFAULT_ORGANIZATION_ID)
        
        await callback.message.edit_text(
            t('booking_branch'),
            reply_markup=get_branches_keyboard(branches)
        )
        await state.set_state(BookingStates.branch)
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data.startswith('branch:'), BookingStates.branch)
async def select_branch(callback: CallbackQuery, state: FSMContext, t: callable):
    """Select branch"""
    branch_id = int(callback.data.split(':')[1])
    await state.update_data(branch_id=branch_id)
    
    # Get services for this branch
    try:
        services = await api_client.get_services(branch_id)
        
        await callback.message.edit_text(
            t('booking_service'),
            reply_markup=get_services_keyboard(services)
        )
        await state.set_state(BookingStates.service)
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data.startswith('service:'), BookingStates.service)
async def select_service(callback: CallbackQuery, state: FSMContext, t: callable):
    """Select service"""
    service_id = int(callback.data.split(':')[1])
    await state.update_data(service_id=service_id)
    
    # Get doctors for this service
    try:
        doctors = await api_client.get_doctors(service_id)
        
        await callback.message.edit_text(
            t('booking_doctor'),
            reply_markup=get_doctors_keyboard(doctors)
        )
        await state.set_state(BookingStates.doctor)
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data.startswith('doctor:'), BookingStates.doctor)
async def select_doctor(callback: CallbackQuery, state: FSMContext, t: callable):
    """Select doctor"""
    doctor_id = int(callback.data.split(':')[1])
    await state.update_data(doctor_id=doctor_id)
    
    # Show calendar
    today = date.today()
    await callback.message.edit_text(
        t('booking_date'),
        reply_markup=get_calendar_keyboard(today.year, today.month)
    )
    await state.set_state(BookingStates.date)


@router.callback_query(F.data.startswith('cal:'), BookingStates.date)
async def navigate_calendar(callback: CallbackQuery, state: FSMContext):
    """Navigate calendar"""
    parts = callback.data.split(':')
    action = parts[1]
    year = int(parts[2])
    month = int(parts[3])
    
    if action == 'prev':
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    elif action == 'next':
        month += 1
        if month > 12:
            month = 1
            year += 1
    
    await callback.message.edit_reply_markup(
        reply_markup=get_calendar_keyboard(year, month)
    )


@router.callback_query(F.data.startswith('date:'), BookingStates.date)
async def select_date(callback: CallbackQuery, state: FSMContext, t: callable):
    """Select date"""
    date_str = callback.data.split(':')[1]
    await state.update_data(date=date_str)
    
    # Get time slots
    data = await state.get_data()
    doctor_id = data['doctor_id']
    
    try:
        slots = await api_client.get_slots(doctor_id, date_str)
        
        if not any(s['available'] for s in slots):
            await callback.answer(t('booking_no_slots'), show_alert=True)
            return
        
        await callback.message.edit_text(
            t('booking_time'),
            reply_markup=get_time_slots_keyboard(slots)
        )
        await state.set_state(BookingStates.time)
    except Exception:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data.startswith('time:'), BookingStates.time)
async def select_time(callback: CallbackQuery, state: FSMContext, t: callable, language: str):
    """Select time"""
    time_str = callback.data.split(':')[1]
    await state.update_data(time=time_str)
    
    # Show confirmation
    data = await state.get_data()
    
    # Format confirmation message (simplified - in production get full details from API)
    confirmation_text = t('booking_confirm',
        branch="Филиал",
        doctor="Врач",
        date=data['date'],
        time=time_str,
        price="0 ₸"
    )
    
    await callback.message.edit_text(
        confirmation_text,
        reply_markup=get_confirmation_keyboard(language)
    )
    await state.set_state(BookingStates.confirmation)


@router.callback_query(F.data == 'confirm:yes', BookingStates.confirmation)
async def confirm_booking(callback: CallbackQuery, state: FSMContext, t: callable, telegram_user: any, language: str):
    """Confirm booking"""
    data = await state.get_data()
    
    # Create appointment via API
    appointment_data = {
        'telegram_user_id': telegram_user.id,
        'employee_id': data['doctor_id'],
        'service_id': data['service_id'],
        'branch_id': data['branch_id'],
        'date': data['date'],
        'time': data['time'],
    }
    
    try:
        result = await api_client.create_appointment(appointment_data)
        
        # Generate ICS file
        ics_content = generate_ics_file(result)
        
        await callback.message.edit_text(t('booking_success'))
        
        # Send ICS file
        from aiogram.types import BufferedInputFile
        ics_file = BufferedInputFile(
            ics_content.encode('utf-8'),
            filename='appointment.ics'
        )
        await callback.message.answer_document(ics_file)
        
        # Back to main menu
        await callback.message.answer(
            t('main_menu'),
            reply_markup=get_main_menu_keyboard(language)
        )
        
        await state.clear()
    except Exception as e:
        await callback.answer(t('error_general'), show_alert=True)


@router.callback_query(F.data == 'confirm:no', BookingStates.confirmation)
async def cancel_booking(callback: CallbackQuery, state: FSMContext, t: callable, language: str):
    """Cancel booking"""
    await callback.message.edit_text(t('booking_cancelled'))
    
    await callback.message.answer(
        t('main_menu'),
        reply_markup=get_main_menu_keyboard(language)
    )
    
    await state.clear()

