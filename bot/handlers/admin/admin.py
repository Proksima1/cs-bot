import json
from asyncio import sleep
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data import *
from loader import dp, client, bot
from utils import *
from states import AdminPanel
from db.sql_commands import *


@dp.callback_query_handler(lambda c: c.data == 'enter_admin_panel', state=None)
async def admin_enter_panel(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await AdminPanel.main.set()
    admins = select_admins()
    await state.set_data(admins)
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
async def mail(cb: types.CallbackQuery):
    await cb.message.answer(
        '✉️ Отправьте сообщение для рассылки:'
    )
    await AdminPanel.get_mail_text.set()


@dp.message_handler(state=AdminPanel.get_mail_text, content_types=types.ContentType.ANY)
async def mail_on(message: types.Message, state: FSMContext):
    add_log('Запущена рассылка')
    if types.ContentType.TEXT == message.content_type:  # Если админ отправил текст
        for user in select_users():
            try:
                await dp.bot.send_message(
                    chat_id=user.user_id,
                    text=message.html_text,
                    parse_mode='MarkdownV2'
                )
                add_log(f'Send message to {user.user_id}')
                await sleep(0.33)
            except Exception as e:
                add_log(str(e))
        else:
            add_log('Рассылка завершена')
            await message.answer(
                '✅ Рассылка завершена!'
            )


    elif types.ContentType.PHOTO == message.content_type:  # Если админ отправил фото
        for user in select_users():
            try:
                await dp.bot.send_photo(
                    chat_id=user.user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.html_text if message.caption else None,
                    parse_mode='MarkdownV2'
                )
                add_log(f'Send message to {user.user_id}')

                await sleep(0.33)
            except Exception as e:
                add_log(str(e))
                # pass
        else:
            add_log('Рассылка завершена')
            await message.answer(
                '✅ Рассылка завершена!'
            )

    elif types.ContentType.VIDEO == message.content_type:  # Если админ отправил видео
        for user in select_users():
            try:
                await dp.bot.send_video(
                    chat_id=user.user_id,
                    video=message.video.file_id,
                    caption=message.html_text if message.caption else None,
                    parse_mode='MarkdownV2'
                )
                add_log(f'Send message to {user.user_id}')

                await sleep(0.33)
            except Exception as e:
                add_log(str(e))
                # pass
        else:
            add_log('Рассылка завершена')

            await message.answer(
                '✅ Рассылка завершена!'
            )

    elif types.ContentType.ANIMATION == message.content_type:  # Если админ отправил gif
        for user in select_users():
            try:
                await dp.bot.send_animation(
                    chat_id=user.user_id,
                    animation=message.animation.file_id,
                    caption=message.html_text if message.caption else None,
                    parse_mode='MarkdownV2'
                )
                add_log(f'Send message to {user.user_id}')

                await sleep(0.33)
            except Exception as e:
                add_log(str(e))
        else:
            add_log('Рассылка завершена')

            await message.answer(
                '✅ Рассылка завершена!'
            )

    else:
        await message.answer(
            '❗️ Данный формат контента не поддерживается для рассылки!'
        )
        add_log('Данный формат контента не поддерживается для рассылки!')
    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'leave_admin_panel', state=AdminPanel.main)
async def admin_leave_panel(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.finish()
    await callback_query.message.answer('Вы вышли из админ-панели.')
    # state = Dispatcher.get_current().current_state()
    # await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'admin_list_admins', state=AdminPanel.main)
async def admin_list_admins(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    admins = await state.get_data()
    admins = [f"➖ {admin}\n" for admin in admins]
    await callback_query.message.answer(f"Админы:\n{''.join(admins)}")


@dp.callback_query_handler(lambda c: c.data == 'admin_delete_admin', state=AdminPanel.main)
async def admin_delete_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await AdminPanel.delete_admin.set()
    await callback_query.message.answer('Пришлите id пользователя,'
                                        ' которого хотите удалить пользователя:')


@dp.message_handler(state=AdminPanel.delete_admin)
async def admin_delete_admin_from_db(message: types.Message, state: FSMContext):
    admins = await state.get_data()
    id = int(message.text)
    if id not in admins:
        await message.answer('Пользователь с такими данными не найден в списке админов')
    else:
        admins.pop(admins.index(id))
        await state.set_data(admins)
        delete_admin(id)
        await message.answer(f'✅ Теперь пользователь с telegram id "{message.text}" не имеет доступ к админ-панеле')
        await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'admin_add_admin', state=AdminPanel.main)
async def admin_add_admin(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await AdminPanel.add_admin.set()
    await callback_query.message.answer('Пришлите id пользователя:')


@dp.message_handler(state=AdminPanel.add_admin)
async def admin_add_admin_in_db(message: types.Message, state: FSMContext):
    admins = await state.get_data()
    id = int(message.text)
    if id in admins:
        await message.answer('Такой пользователь уже является админом.')
    else:
        admins.append(id)
        await state.set_data(admins)
        set_admin(id)
        await message.answer(f'✅ Теперь пользователь с telegram id "{message.text}" имеет доступ к админ-панеле')
        await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'admin_get_vip', state=AdminPanel.main)
async def admin_get_vip(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await AdminPanel.get_steam_id.set()
    await callback_query.message.answer('Пришлите steam_id в любом виде, на который требуется выдать VIP.')


@dp.message_handler(state=AdminPanel.get_steam_id)
async def admin_get_steam_id(message: types.Message, state: FSMContext):
    data = await search_for_steam_id(message.text, search_steam_id_error)
    if data['status'] == 'error':
        await message.answer(search_steam_id_error)
    else:
        steam_id = data['text']
        if steam_id != 0:
            write_data(USERS_FILE_PATH, steam_id)
            add_log(f'{message.from_user.id} выдал VIP "{steam_id}"')
            await state.finish()
            await message.answer(vip_set)
        else:
            await message.answer(steam_id_not_found)
