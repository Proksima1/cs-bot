import asyncio
import logging
import json
import os.path

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.utils.exceptions import *
from bs4 import BeautifulSoup
from yoomoney import Client

from config import *
from utils import *

client = Client(YOOMONEY_TOKEN)
bot = Bot(token=TOKEN)
logging.basicConfig(
    filename='errors.log',
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    level=logging.INFO
)
dp = Dispatcher(bot, storage=MemoryStorage())
back_button = InlineKeyboardButton("⬅️ Назад", callback_data='go_back')


async def on_startup(_):
    global ADMINS
    print("Bot started!")
    if os.path.isfile(ADMINS_FILE):
        with open(ADMINS_FILE, encoding='utf-8') as reader:
            ADMINS = json.loads(reader.read())['admins']
    else:
        with open(ADMINS_FILE, 'a+', encoding='utf-8') as writer:
            writer.write(json.dumps({'admins': ADMINS}))
    print('Admins loaded successfully!')


async def shutdown(_):
    pass


@dp.message_handler(commands=['help'], state="*")
async def help(message: types.Message):
    await message.answer(help_message, parse_mode='html')


@dp.message_handler(state=None)
async def send_welcome(message: types.Message):
    buttons_row = InlineKeyboardMarkup()
    yes_button = InlineKeyboardButton('Да', callback_data='yes')
    no_button = InlineKeyboardButton('Нет', callback_data='no')
    buttons_row.add(yes_button, no_button)
    if message.from_user.username in ADMINS or str(message.from_user.id) in ADMINS:
        buttons_row.row(InlineKeyboardButton('Войти в админ панель', callback_data='enter_admin_panel'))
    await message.answer(
        f"👋Привет. Хочешь VIP? Стоимость VIP <b>{VIP_COST}руб</b>. Нужен твой SteamID в любом формате, например:"
        " \n\nSteam ID: STEAM_0:1:998772\nSteam3: [U:1:1997545]\nCommunity ID: 76561197962263273", parse_mode='html')
    await message.answer('Знаешь свой SteamID?', reply_markup=buttons_row)


@dp.callback_query_handler(lambda c: c.data == 'enter_admin_panel', state=None)
async def admin_enter_panel(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await AdminPanel.main.set()
    set_steam_id = InlineKeyboardButton('Установить вип по steam_id 🛠️', callback_data='admin_get_vip')
    do_mail = InlineKeyboardButton('Сделать рассылку', callback_data='do_mail')  # TODO
    add_admin = InlineKeyboardButton('Добавить админа ➕', callback_data='admin_add_admin')
    list_admins = InlineKeyboardButton('Посмотреть список 🔍', callback_data='admin_list_admins')
    delete_admin = InlineKeyboardButton('Удалить админа ➖', callback_data='admin_delete_admin')
    leave_admin_panel = InlineKeyboardButton('Выйти из админ панели', callback_data='leave_admin_panel')
    admin_buttons = InlineKeyboardMarkup()
    admin_buttons.row(set_steam_id, do_mail)
    admin_buttons.row(add_admin, list_admins)
    admin_buttons.row(delete_admin)
    admin_buttons.row(leave_admin_panel)
    await callback_query.message.answer('Добро пожаловать в админ панель. Выберите действие:',
                                        reply_markup=admin_buttons)


@dp.callback_query_handler(lambda c: c.data == 'do_mail', state=AdminPanel.main)
async def do_mail(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await AdminPanel.mail_menu.set()
    kb = InlineKeyboardMarkup()
    back = InlineKeyboardButton('⬅️ Назад', callback_data='')
    with_photo = InlineKeyboardButton('🖼 С изображением', callback_data='mail_message 1')
    without_photo = InlineKeyboardButton('Без изображением', callback_data='mail_message 0')
    kb.row(without_photo, with_photo)
    await callback_query.message.edit_text('Выберите тип рассылки', reply_markup=kb)


@dp.callback_query_handler(lambda c: 'mail_message' in c.data, state=AdminPanel.mail_menu)
async def mail_message(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    print(callback_query.data)
    await callback_query.message.answer('Пришлите текст, который хотите разослать')
    if callback_query.data.split()[1] == '0':
        await AdminPanel.get_mail_message_text.set()
    else:
        await AdminPanel.get_mail_message_text_with_photo.set()


@dp.callback_query_handler(lambda c: c.data == 'leave_admin_panel', state=AdminPanel.main)
async def admin_leave_panel(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.finish()
    await callback_query.message.answer('Вы вышли из админ-панели.')
    # state = Dispatcher.get_current().current_state()
    # await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'admin_list_admins', state=AdminPanel.main)
async def admin_delete_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    admins = [f"➖ {admin}\n" for admin in ADMINS]
    await callback_query.message.answer(f"Админы:\n{''.join(admins)}")


@dp.callback_query_handler(lambda c: c.data == 'admin_delete_admin', state=AdminPanel.main)
async def admin_delete_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await AdminPanel.delete_admin.set()
    await callback_query.message.answer('Пришлите username(без @) или id пользователя,'
                                        ' которого хотите удалить пользователя:')


@dp.message_handler(state=AdminPanel.delete_admin)
async def admin_delete_admin_from_file(message: types.Message, state: FSMContext):
    global ADMINS
    if message.text not in ADMINS:
        await message.answer('Пользователь с такими данными не найден в списке админов')
    else:
        ADMINS.pop(ADMINS.index(message.text))
        with open(ADMINS_FILE, 'w+') as writer:
            writer.write(json.dumps({'admins': ADMINS}))
        await message.answer(f'✅ Теперь пользователь с никнеймом/id "{message.text}" не имеет доступ к админ-панеле')
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'admin_add_admin', state=AdminPanel.main)
async def admin_add_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await AdminPanel.add_admin.set()
    await callback_query.message.answer('Пришлите username(без @) или id пользователя:')


@dp.message_handler(state=AdminPanel.add_admin)
async def admin_add_admin_in_file(message: types.Message, state: FSMContext):
    global ADMINS
    if message.text in ADMINS:
        await message.answer('Такой пользователь уже является админом.')
    else:
        ADMINS.append(message.text)
        with open(ADMINS_FILE, 'w+') as writer:
            writer.write(json.dumps({'admins': ADMINS}))
        await message.answer(f'✅ Теперь пользователь с никнеймом/id "{message.text}" имеет доступ к админ-панеле')
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'admin_get_vip', state=AdminPanel.main)
async def admin_get_vip(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await AdminPanel.get_steam_id.set()
    await callback_query.message.answer('Пришлите steam_id в любом виде, на который требуется выдать VIP.')


@dp.message_handler(state=AdminPanel.get_steam_id)
async def admin_get_steam_id(message: types.Message, state: FSMContext):
    data = await search_for_steam_id(message.text)
    if data['status'] == 'error':
        await message.answer(search_steam_id_error)
    else:
        steam_id = data['text']
        if steam_id != 0:
            write_data(USERS_FILE_PATH, steam_id)
            await state.finish()
            await message.answer(vip_set)
        else:
            await message.answer(steam_id_not_found)


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


async def search_for_steam_id(id_text):
    loop = asyncio.get_event_loop()
    client = aiohttp.ClientSession(loop=loop, trust_env=True)
    resp = await client.post('https://steamid.io/lookup', data={'input': id_text})
    if resp.status != 200:
        return {'status': 'error', 'text': search_steam_id_error}
    text_response = await resp.text()
    soup = BeautifulSoup(text_response, 'html.parser')
    try:
        steam_id = soup.find('dl', class_='panel-body').find_all('dd', class_='value')[0].find('a').text
        return {'status': 'success',
                'text': steam_id}
    except AttributeError:
        return {'status': 'success',
                'text': '0'}


@dp.message_handler(state=VipPurchase.wait_for_steam_id)
async def get_steam_id(message: types.Message, state: FSMContext):
    data = await search_for_steam_id(message.text)
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


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=shutdown)
