"""
Booking FSM states
"""
from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    """Appointment booking flow states"""
    branch = State()
    service = State()
    doctor = State()
    date = State()
    time = State()
    confirmation = State()
    payment = State()

