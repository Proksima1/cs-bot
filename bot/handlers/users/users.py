import asyncio

import aiohttp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import BotBlocked
from bs4 import BeautifulSoup
from data import *
from loader import dp, client, bot
from states import VipPurchase
from utils import *
from db.sql_commands import *



ADMINS = []
back_button = InlineKeyboardButton("⬅️ Назад", callback_data='go_back')


@dp.message_handler(commands=['help'], state="*")
async def help(message: types.Message):
    await message.answer(help_message, parse_mode='html')


@dp.message_handler(CommandStart(), state=None)
async def send_welcome(message: types.Message):
    f, s = message.from_user.first_name, message.from_user.last_name
    name = f
    if s is not None:
        name += f' {s}'
    print(name)
    register_user(message.from_user.id, name, False)
    buttons_row = InlineKeyboardMarkup()
    yes_button = InlineKeyboardButton('Да', callback_data='yes')
    no_button = InlineKeyboardButton('Нет', callback_data='no')
    buttons_row.add(yes_button, no_button)
    admins = select_admins()
    if message.from_user.id in admins:
        buttons_row.row(InlineKeyboardButton('Войти в админ панель', callback_data='enter_admin_panel'))
    await message.answer(
        f"👋Привет. Хочешь VIP? Стоимость VIP <b>{VIP_COST}руб</b>. Нужен твой SteamID в любом формате, например:"
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
    data = await search_for_steam_id(message.text, search_steam_id_error)
    if data['status'] == 'error':
        await message.answer(data['error'])
        for admin in ADMINS:
            await bot.send_message(admin, '<b>Ошибка при работе бота!\nС сайтом steamid проблема</b>',
                                   parse_mode='html')
    else:
        steam_id = data['text']
        if steam_id != '0':
            s = await async_generate_random_string(10)
            buttons_row = InlineKeyboardMarkup()
            async with Quickpay(
                    receiver=PAYMENT_RECEIVER,
                    quickpay_form="shop",
                    targets="Покупка VIP",
                    paymentType="SB",
                    label=s,
                    sum=VIP_COST,
            ) as quickpay:
                async with state.proxy() as data:
                    data['steam_id'] = steam_id
                    data['label'] = s
                    data['redirect_url'] = quickpay.redirected_url
                buttons_row.add(InlineKeyboardButton('Перейти в youmoney',
                                                     url=quickpay.redirected_url))
                buttons_row.add(InlineKeyboardButton('🔍 Проверить оплату', callback_data='check_payment'))
                buttons_row.add(back_button)
                try:
                    await message.answer(f'Теперь произведи оплату. \nID вашего платежа: <code>{s}</code>',
                                         reply_markup=buttons_row,
                                         parse_mode='html')
                    await VipPurchase.wait_for_payment.set()
                except BotBlocked:
                    pass
        else:
            await message.answer(steam_id_not_found)


@dp.callback_query_handler(lambda c: c.data == 'go_back', state=VipPurchase.wait_for_payment)
async def go_back(query: types.CallbackQuery):
    await VipPurchase.wait_for_steam_id.set()
    await bot.answer_callback_query(query.id)
    kb = InlineKeyboardMarkup().add(InlineKeyboardButton('⬅️ Назад', callback_data='back_to_main'))
    try:
        await query.message.answer('Пришли мне свой Steam ID.', reply_markup=kb)
    except BotBlocked:
        pass


@dp.callback_query_handler(lambda c: c.data == 'back_to_main', state=VipPurchase.wait_for_steam_id)
async def back_to_main(query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.answer_callback_query(query.id)
    await query.message.answer('Вы в главном меню')


async def check_pay(message, label: str, state, steam_id):
    for i in range(20):
        history = client.operation_history(label=label)
        for operation in history.operations:
            if operation.status.lower() == 'success' and operation.label == label:
                write_data(USERS_FILE_PATH, steam_id)
                try:
                    await message.edit_reply_markup()
                    message_text = payment_message.format(label, 'оплачено✅')
                    add_log(f'Куплен VIP на "{steam_id}"')
                    await message.edit_text(message_text, parse_mode='html')
                    await state.finish()
                    await message.answer(vip_set)
                except BotBlocked:
                    pass
                break
        await asyncio.sleep(2)
    else:
        try:
            message_text = payment_message.format(label, 'не найдено❌')
            await message.edit_text(message_text, parse_mode='html')
            await message.edit_reply_markup(InlineKeyboardMarkup().add(
                InlineKeyboardButton('🔍 Проверить снова',
                                     callback_data='check_payment_again'),
                back_button
            ))
        except BotBlocked:
            pass


@dp.callback_query_handler(lambda c: c.data == 'check_payment', state=VipPurchase.wait_for_payment)
async def check_payment(query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        d = data.as_dict()
        label = d['label']
        redir_url = d['redirect_url']
        steam_id = d['steam_id']
    try:
        await query.message.edit_reply_markup(InlineKeyboardMarkup().add(InlineKeyboardButton('Перейти в youmoney',
                                                                                              url=redir_url)))
        message_text = payment_message.format(label, 'проверяется🔄')
        message = await bot.send_message(query.from_user.id, message_text, parse_mode='html')
        await check_pay(message, label, state, steam_id)
    except BotBlocked:
        pass


@dp.callback_query_handler(lambda c: c.data == 'check_payment_again', state=VipPurchase.wait_for_payment)
async def check_payment_again(query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(query.id)
    async with state.proxy() as data:
        d = data.as_dict()
        label = d['label']
        steam_id = d['steam_id']
    try:
        message_text = payment_message.format(label, 'проверяется🔄')
        await query.message.edit_text(message_text, parse_mode='html')
    except BotBlocked:
        pass
    await check_pay(query.message, label, state, steam_id)