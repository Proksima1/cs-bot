import os
from os.path import join, dirname

from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), 'worker.env')
load_dotenv(dotenv_path)

LOG_PATH = os.environ.get('LOG_PATH')
SERVER = os.environ.get('SERVER')
USERNAME = os.environ.get('FTP_USERNAME_CONNECT')
PASSWORD = os.environ.get('FTP_PASSWORD_CONNECT')










