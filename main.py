import asyncio
import os
from os.path import join, dirname

import requests
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from yoomoney import Quickpay, Client

from states import *
from utils import generate_random_string, write_data

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TOKEN = os.environ.get('TOKEN')
PAYMENT_RECEIVER = os.environ.get('PAYMENT_RECEIVER')
VIP_COST = int(os.environ.get("VIP_COST"))
YOOMONEY_TOKEN = os.environ.get("YOOMONEY_TOKEN")
client = Client(YOOMONEY_TOKEN)
QIWI_TOKEN = '3f7f2393d867336d833d3ae19dd05dbf'
QIWI_ACCOUNT = '+79859772201'
FILE_PATH = os.environ.get('FILE_PATH')
s = requests.Session()
s.headers['authorization'] = 'Bearer ' + QIWI_TOKEN
parameters = {'rows': '50'}
h = s.get('https://edge.qiwi.com/payment-history/v1/persons/' + QIWI_ACCOUNT + '/payments', params=parameters)
# req = json.loads(h.text)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


async def on_startup(_):
    print("Bot started!")


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
    await bot.send_message(callback_query.from_user.id, 'Тогда напиши его мне и произведи оплату :)')
    await VipPurchase.wait_for_steam_id.set()


@dp.callback_query_handler(lambda c: c.data == 'no', state=None)
async def no_button_clicked(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Зайди на сервер, напиши в консоль status.'
                                                        ' Твой SteamID будет в формате [U:х:ххххххх] - это то, что нужно')
    await VipPurchase.wait_for_steam_id.set()


@dp.message_handler(state=VipPurchase.wait_for_steam_id)
async def get_steam_id(message: types.Message, state: FSMContext):
    resp = requests.post('https://steamid.io/lookup', data={'input': message.text}).text
    soup = BeautifulSoup(resp, 'html.parser')
    try:
        steam_id = soup.find('dl', class_='panel-body').find_all('dd', class_='value')[0].find('a').text
    except AttributeError:
        await message.answer("Такого steam_id не найдено, попробуй ввести другой.")
    else:
        s = generate_random_string(10)
        async with state.proxy() as data:
            data['steam_id'] = steam_id
            data['label'] = s
        buttons_row = InlineKeyboardMarkup()
        quickpay = Quickpay(
            receiver=PAYMENT_RECEIVER,
            quickpay_form="shop",
            targets="Покупка VIP",
            paymentType="SB",
            label=s,
            sum=VIP_COST,
        )
        buttons_row.add(InlineKeyboardButton('Перейти в youmoney',
                                             url=quickpay.redirected_url))
        buttons_row.add(InlineKeyboardButton('Проверить оплату', callback_data='check_payment'))
        buttons_row.add(InlineKeyboardButton("Назад", callback_data='go_back'))
        await message.answer(f'Теперь произведи оплату. \nID вашего платежа: {s}', reply_markup=buttons_row)
        await VipPurchase.wait_for_payment.set()


@dp.callback_query_handler(lambda c: c.data == 'go_back', state=VipPurchase.wait_for_payment)
async def go_back(query: types.CallbackQuery):
    await VipPurchase.wait_for_steam_id.set()
    await query.message.answer('Пришли мне свой Steam ID.')


@dp.callback_query_handler(lambda c: c.data == 'check_payment', state=VipPurchase.wait_for_payment)
async def check_payment(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        label = data.as_dict()['label']
    message = await bot.send_message(query.from_user.id, f'Платёж\n\nID платежа - *{label}*\n'
                                                         f'Сумма платежа - *{VIP_COST} руб.*\n'
                                                         f'Статус платежа - проверяется🔄', parse_mode='markdown')
    history = client.operation_history(label=label)
    # for operation in history.operations:
    # if operation.status.lower() == 'success' and operation.label == label and operation.amount >= VIP_COST:
    async with state.proxy() as data:
        write_data(FILE_PATH, data.as_dict()['steam_id'])
    await asyncio.sleep(2)
    await message.edit_text(f'Платёж\n\nID платежа - *{label}*\n'
                            f'Сумма платежа - *{VIP_COST} руб.*\n'
                            f'Статус платежа - оплачено✅', parse_mode='markdown')
    await state.finish()
    await message.answer('VIP-статус выдан ;) Приятной игры!')


# @dp.message_handler(state=VipPurchase.wait_for_payment)
# async def accept_payment(message: types.Message, state: FSMContext):
#     await message.answer("Оплата произведена успешно.")
#     await state.finish()


if __name__ == '__main__':
    # history = client.operation_history(label="a1b2c3d4e5")
    # print(history.operations)
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
