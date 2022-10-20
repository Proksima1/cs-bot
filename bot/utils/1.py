import ftplib
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
SERVER = os.environ.get('SERVER')
USERNAME = os.environ.get('FTP_USERNAME_CONNECT')
PASSWORD = os.environ.get('FTP_PASSWORD_CONNECT')
session = ftplib.FTP(SERVER, USERNAME, PASSWORD)