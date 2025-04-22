from aiogram.fsm.state import State, StatesGroup
__all__ = ['FSMMainState', 'FSMAuthState']


class FSMMainState(StatesGroup):
    waiting_rules_accept = State()
    main_menu = State()
    settings_menu = State()
    find_info = State()
    create_dossier = State()
    admin_menu = State()


class FSMAuthState(StatesGroup):
    start_auth = State()
    waiting_for_phone = State()
    waiting_for_code = State()
    waiting_for_password = State()
    successful_auth = State()
