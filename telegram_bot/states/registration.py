"""
Registration FSM states
"""
from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Registration flow states"""
    language = State()
    first_name = State()
    last_name = State()
    middle_name = State()
    phone = State()
    birth_date = State()
    sex = State()
    iin = State()
    consents = State()

