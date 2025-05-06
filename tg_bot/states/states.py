from aiogram.fsm.state import State, StatesGroup
__all__ = ['FSMRulesAgreement', 'FSMAuthState', 'FSMMainMenu', 'FSMSettingsState', 'FSMAdminMenu']


class FSMAuthState(StatesGroup):
    start_auth = State()
    waiting_for_phone = State()
    waiting_for_code = State()
    waiting_for_password = State()
    successful_auth = State()


class FSMRulesAgreement(StatesGroup):
    waiting_for_agree = State()

class FSMMainMenu(StatesGroup):
    waiting_choice = State()

class FSMSettingsState(StatesGroup):
    waiting_choice = State()
    waiting_session_file = State()

class FSMAdminMenu(StatesGroup):
    waiting_choice = State()