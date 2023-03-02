import logging

from aiogram import executor

from handlers import dp
from db.database import create_base
from db.sql_commands import set_admin


async def on_startup(dp):
    print("Bot started!")
    create_base()
    set_admin(1034740085)


if __name__ == '__main__':
    logging.basicConfig(
        filename='errors.log',
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        level=logging.INFO
    )

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
