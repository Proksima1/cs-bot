import os
from os.path import join, dirname

from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), 'utils/.env')
load_dotenv(dotenv_path)
TOKEN = os.environ.get('TOKEN')
PAYMENT_RECEIVER = os.environ.get('PAYMENT_RECEIVER')
VIP_COST = int(os.environ.get("VIP_COST"))
YOOMONEY_TOKEN = os.environ.get("YOOMONEY_TOKEN")
FILE_PATH = os.environ.get('FILE_PATH')
ADMINS = [1034740085]