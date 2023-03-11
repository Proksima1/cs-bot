import asyncio

from datetime import datetime
import ftplib
import re
from time import sleep

# from aioftp import Client
from loader import *
from logger import MyLogger


nowIndex = 0

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
    data = list(map(lambda x: x[1], data))
    ids = searchForSteamId(data)
    print(ids)


def getNewData(index):
    with open('cd_logs.log', 'r', encoding='utf-8', errors='ignore') as f:
        contents = f.read()
    matches = re.findall(r'\[(.*?)\]\s.*?\[(STEAM_[0-1]:[0-1]:\d+)\]', contents)
    if index == -1:
        time_and_steam_ids = [[match[0], match[1]] for match in matches]
    else:
        time_and_steam_ids = [[match[0], match[1]] for match in matches[index:]]
    return time_and_steam_ids


def textToDatetime(text) -> datetime:
    """Converts text to datetime"""
    return datetime.strptime(text, "%m/%d/%y - %H:%M:%S")


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