from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminPanel(StatesGroup):
    main = State()
    get_steam_id = State()
    add_admin = State()
    delete_admin = State()
    get_mail = State()
    get_mail_text = State()