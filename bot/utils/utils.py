import ftplib
import os
import random
import re
import string
from datetime import datetime
from datetime import timedelta
from os.path import join, dirname
from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
SERVER = os.environ.get('SERVER')
USERNAME = os.environ.get('FTP_USERNAME_CONNECT')
PASSWORD = os.environ.get('FTP_PASSWORD_CONNECT')


async def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string


def flatten(lst):
    for v in lst:
        if isinstance(v, list):
            yield from flatten(v)
        else:
            yield v


def update_time(time):
    if int(time) == 0:
        today = datetime.now()
        days = calendar.monthrange(today.year, today.month)[1]
        next_month_date = int((today + timedelta(days=days)).timestamp())
    else:
        d = datetime.utcfromtimestamp(int(time))
        days = calendar.monthrange(d.year, d.month)[1]
        next_month_date = int((d + timedelta(days=days)).timestamp())
    return next_month_date


def grabFile(session: ftplib.FTP, filename):
    with open(filename, 'wb') as file:
        session.retrbinary('RETR ' + filename, file.write, 1024)


def placeFile(session: ftplib.FTP, filename):
    session.storbinary('STOR ' + filename, open(filename, 'rb'))


def write_data(path_to_file: str, user_id: str):
    session = ftplib.FTP(SERVER, USERNAME, PASSWORD)
    session.cwd('/addons/sourcemod/data/vip/')
    s = ['"Users"']
    grabFile(session, path_to_file)
    with open(path_to_file, encoding='utf-8', errors='replace') as f:
        text = f.read()
        print(text)
        current_level = 0
        found = False
        for line in text.splitlines():
            l = line.strip()
            print(l)
            if l == '{':
                current_level += 1
                s.append(line)
                continue
            elif l == '}':
                current_level -= 1
                s.append(line)
                continue
            if current_level == 1:
                steam_id = l[1:-1]
                s.append(line)
                if steam_id == user_id:
                    found = True
            elif current_level == 2:
                m = re.search(r'"(.+?)"\s+"(.+?)"', l)
                key, value = m.group(1), m.group(2)
                if found and key == 'expires':
                    s.append(line.replace(value, str(update_time(value))))
                    found = None
                else:
                    s.append(line)
        if found is not None:
            spis = [f'\t"{user_id}"', "\t{", f'\t\t"name"\t\t"{generate_random_string(10)}"',
                    f'\t\t"expires"\t\t"{str(update_time(0))}"', '\t\t"group"\t\t"GOLD"', '\t}']
            s.insert(-1, spis)

        s = "\n".join(flatten(s))
    with open(path_to_file, mode='w', encoding='utf-8') as w:
        w.write(s)
    placeFile(session, path_to_file)
    session.close()
    os.remove(path_to_file)