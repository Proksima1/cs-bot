import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.exceptions import *
from bs4 import BeautifulSoup
from yoomoney import Quickpay, Client
from utils import *


client = Client(YOOMONEY_TOKEN)
bot = Bot(token=TOKEN)
logging.basicConfig(
    filename='errors.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)
dp = Dispatcher(bot, storage=MemoryStorage())


async def on_startup(_):
    print("Bot started!")


async def shutdown(_):
    pass


@dp.message_handler(state=None)
async def send_welcome(message: types.Message):
    yes_button = InlineKeyboardButton('Да', callback_data='yes')
    no_button = InlineKeyboardButton('Нет', callback_data='no')
    buttons_row = InlineKeyboardMarkup().add(yes_button, no_button)
    await message.answer(
        f"Привет. Хочешь VIP? Стоимость VIP <b>{VIP_COST}руб</b>. Нужен твой SteamID в любом формате, например:"
        " \n\nSteam ID: STEAM_0:1:998772\nSteam3: [U:1:1997545]\nCommunity ID: 76561197962263273", parse_mode='html')
    await message.answer('Знаешь свой SteamID?', reply_markup=buttons_row)


@dp.callback_query_handler(lambda c: c.data == 'yes', state=None)
async def yes_button_clicked(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    try:
        await bot.send_message(callback_query.from_user.id, 'Тогда напиши его мне и произведи оплату :)')
        await VipPurchase.wait_for_steam_id.set()
    except BotBlocked:
        pass


@dp.callback_query_handler(lambda c: c.data == 'no', state=None)
async def no_button_clicked(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    try:
        await bot.send_message(callback_query.from_user.id, 'Зайди на сервер, напиши в консоль <code>status</code>. '
                                                            'Твой SteamID будет в формате [U:х:ххххххх] - это то, что нужно.'
                                                            'Пришли его сюда', parse_mode='html')
        await VipPurchase.wait_for_steam_id.set()
    except BotBlocked:
        pass


@dp.message_handler(state=VipPurchase.wait_for_steam_id)
async def get_steam_id(message: types.Message, state: FSMContext):
    resp = requests.post('https://steamid.io/lookup', data={'input': message.text})
    if resp.status_code != 200:
        await message.answer('🔧В работе бота возникли технические неполадки, пожалуйста, повторите попытку позже!')
        for admin in ADMINS:
            await bot.send_message(admin, '<b>Ошибка при работе бота!\nС сайтом steamid проблема</b>', parse_mode='html')
        return
    text_response = resp.text
    soup = BeautifulSoup(text_response, 'html.parser')
    try:
        steam_id = soup.find('dl', class_='panel-body').find_all('dd', class_='value')[0].find('a').text
    except AttributeError:
        await message.answer("Такого steam_id не найдено, попробуй ввести другой.")
    else:
        s = generate_random_string(10)
        buttons_row = InlineKeyboardMarkup()
        quickpay = Quickpay(
            receiver=PAYMENT_RECEIVER,
            quickpay_form="shop",
            targets="Покупка VIP",
            paymentType="SB",
            label=s,
            sum=VIP_COST,
        )
        async with state.proxy() as data:
            data['steam_id'] = steam_id
            data['label'] = s
            data['redirect_url'] = quickpay.redirected_url
        buttons_row.add(InlineKeyboardButton('Перейти в youmoney',
                                             url=quickpay.redirected_url))
        buttons_row.add(InlineKeyboardButton('Проверить оплату', callback_data='check_payment'))
        buttons_row.add(InlineKeyboardButton("Назад", callback_data='go_back'))
        try:
            await message.answer(f'Теперь произведи оплату. \nID вашего платежа: <code>{s}</code>', reply_markup=buttons_row,
                                 parse_mode='html')
            await VipPurchase.wait_for_payment.set()
        except BotBlocked:
            pass


@dp.callback_query_handler(lambda c: c.data == 'go_back', state=VipPurchase.wait_for_payment)
async def go_back(query: types.CallbackQuery):
    await VipPurchase.wait_for_steam_id.set()
    try:
        await query.message.answer('Пришли мне свой Steam ID.')
    except BotBlocked:
        pass


async def check_pay(message, label: str, state, steam_id):
    for i in range(20):
        history = client.operation_history(label=label)
        for operation in history.operations:
            if operation.status.lower() == 'success' and operation.label == label:
                write_data(FILE_PATH, steam_id)
                try:
                    await message.edit_reply_markup()
                    message_text = payment.format(label, 'оплачено✅')
                    await message.edit_text(message_text, parse_mode='html')
                    await state.finish()
                    await message.answer('VIP-статус выдан ;) Приятной игры!')
                except BotBlocked:
                    pass
                break
        await asyncio.sleep(2)
    else:
        try:
            message_text = payment.format(label, 'не найдено❌')
            await message.edit_text(message_text, parse_mode='html')
            await message.edit_reply_markup(InlineKeyboardMarkup().add(InlineKeyboardButton('Проверить снова',
                                                                                            callback_data='check_payment_again')))
        except BotBlocked:
            pass


@dp.callback_query_handler(lambda c: c.data == 'check_payment', state=VipPurchase.wait_for_payment)
async def check_payment(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        d = data.as_dict()
        label = d['label']
        redir_url = d['redirect_url']
        steam_id = d['steam_id']
    try:
        await query.message.edit_reply_markup(InlineKeyboardMarkup().add(InlineKeyboardButton('Перейти в youmoney',
                                                                                              url=redir_url)))
        message_text = payment.format(label, 'проверяется🔄')
        message = await bot.send_message(query.from_user.id, message_text, parse_mode='html')
        await check_pay(message, label, state, steam_id)
    except BotBlocked:
        pass


@dp.callback_query_handler(lambda c: c.data == 'check_payment_again', state=VipPurchase.wait_for_payment)
async def check_payment_again(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        d = data.as_dict()
        label = d['label']
        steam_id = d['steam_id']
    try:
        message_text = payment.format(label, 'проверяется🔄')
        await query.message.edit_text(message_text, parse_mode='html')
    except BotBlocked:
        pass
    await check_pay(query.message, label, state, steam_id)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=shutdown)
