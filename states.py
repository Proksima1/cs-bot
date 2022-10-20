from aiogram.dispatcher.filters.state import StatesGroup, State


class VipPurchase(StatesGroup):
    wait_for_steam_id = State()
    wait_for_payment = State()