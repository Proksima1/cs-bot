import os
from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TOKEN = os.environ.get('TOKEN')
PAYMENT_RECEIVER = os.environ.get('PAYMENT_RECEIVER')
VIP_COST = int(os.environ.get("VIP_COST"))
YOOMONEY_TOKEN = os.environ.get("YOOMONEY_TOKEN")
USERS_FILE_PATH = os.environ.get('FILE_PATH')
DATABASE_USERNAME = os.environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DATABASE_IP = os.environ.get('DATABASE_IP')
DATABASE_DB = os.environ.get('DATABASE_DB')
# ADMINS = ['Proksima1', '1982380335']
# ADMINS_FILE = './utils/admins.json'
VERSION = '0.2'
