from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from yoomoney import Client
from data.config import *

client = Client(YOOMONEY_TOKEN)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

