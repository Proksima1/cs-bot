from aiogram.dispatcher.filters.state import StatesGroup, State


class VipPurchase(StatesGroup):
    wait_for_steam_id = State()
    wait_for_payment = State()


class Mailing(StatesGroup):
    get_message = State()


class AdminPanel(StatesGroup):
    main = State()
    get_steam_id = State()
    add_admin = State()
    delete_admin = State()
    mail_menu = State()
    get_mail_message_text = State()
    get_mail_message_text_with_photo = State()