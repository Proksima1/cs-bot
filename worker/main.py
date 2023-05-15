import asyncio
import random
import string
import pytz

from datetime import datetime
import ftplib
import re
from time import sleep

# from aioftp import Client
from loader import *
from logger import MyLogger


nowIndex = None
tz = pytz.timezone('Europe/Moscow')




def grabFile(session: ftplib.FTP, filename):
    with open(filename, 'wb') as file:
        session.retrbinary('RETR ' + filename, file.write, 1024)


def placeFile(session: ftplib.FTP, filename):
    session.storbinary('STOR ' + filename, open(filename, 'rb'))


def doIter():
    # session = ftplib.FTP(SERVER, USERNAME, PASSWORD)
    # download_log(session)
    # download_vip(session)
    data = getNewData(nowIndex)
    print(data)
    data = list(map(lambda x: x[1], data))
    # print(data)
    ids = searchForSteamId(data)
    ids = list(filter(lambda x: not x[1], ids))
    add_steam_ids_to_file(ids)


def getNewData(index):
    global nowIndex
    with open('cd_logs.log', 'r', encoding='utf-8', errors='ignore') as f:
        contents = f.read()
    matches = re.findall(r'\[(.*?)\]\s.*?\[(STEAM_[0-1]:[0-1]:\d+)\]', contents)
    if index is None:
        time_and_steam_ids = [[textToDatetime(match[0]), match[1]] for match in matches]
    else:
        time_and_steam_ids = [[textToDatetime(match[0]), match[1]] for match in matches[index:]]
    nowIndex = len(matches)
    return time_and_steam_ids


def sync_generate_random_name(length):
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string


def add_steam_ids_to_file(steam_ids):
    with open('users.ini', 'r', encoding='utf-8', errors='ignore') as f:
        file_content = f.read()
    last_bracket_index = file_content.rfind("}")
    steam_id_str = "\n".join([f'\t"{sid}"\n\t{{\n\t\t"name"\t\t"{sync_generate_random_name(10)}"\n\t\t"expires"\t\t"0"\n\t\t"group"\t\t"GOLD"\n\t}}' for sid, inFile in steam_ids]) + '\n'
    updated_file_content = file_content[:last_bracket_index] + steam_id_str + file_content[last_bracket_index:]
    with open('users.ini', 'w', encoding='utf-8', errors='ignore') as f:
        f.write(updated_file_content)


def textToDatetime(text) -> datetime:
    """Converts text to datetime"""
    return datetime.strptime(text, "%m/%d/%y - %H:%M:%S").astimezone(tz)


def download_log(session):
    session.cwd(LOG_PATH)
    grabFile(session, 'cd_logs.log')


def download_vip(session):
    session.cwd('vip/')
    grabFile(session, 'users.ini')


def searchForSteamId(steam_ids):
    """Gets list of steam ids, searchs in vip file for ids
       return list of booleans
    """
    with open('users.ini', 'r', encoding='utf-8', errors='ignore') as f:
        file_contents = f.read()
    o = [(steam_id, re.search(steam_id, file_contents) is not None) for steam_id in steam_ids]
    return o


if __name__ == '__main__':
    log = MyLogger()
    log.start_rotate_logging("WorkerLog", os.path.join('', "worker.log"))
    # while True:
    doIter()
    # download_vip()
    # print(searchForSteamId(['STEAM_0:0:456199604', 'STEAM_0:0:45619960412421']))
    # sleep(10)