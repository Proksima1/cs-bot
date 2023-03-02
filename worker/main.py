import asyncio
import ftplib
import re
from time import sleep

from aioftp import Client
from loader import *
from logger import MyLogger


nowIndex = 200

def grabFile(session: ftplib.FTP, filename):
    with open(filename, 'wb') as file:
        session.retrbinary('RETR ' + filename, file.write, 1024)


def placeFile(session: ftplib.FTP, filename):
    session.storbinary('STOR ' + filename, open(filename, 'rb'))


def doIter():
    # session = ftplib.FTP(SERVER, USERNAME, PASSWORD)
    # session.cwd(LOG_PATH)
    # grabFile(session, 'cd_logs.log')
    getNewData(nowIndex)


def getNewData(index):
    # Open the file and read its contents
    with open('cd_logs.log', 'r', encoding='utf-8', errors='ignore') as f:
        contents = f.read()

    # Use regular expressions to extract the time and Steam ID from each line
    matches = re.findall(r'\[(.*?)\]\s.*?\[(STEAM_[0-1]:[0-1]:\d+)\]', contents)
    if index == -1:
        time_and_steam_ids = [(match[0], match[1]) for match in matches]

        # Print the list of time and Steam ID pairs
    else:
        time_and_steam_ids = [(match[0], match[1]) for match in matches[index:]]

        # Print the list of time and Steam ID pairs
    print(len(time_and_steam_ids))




if __name__ == '__main__':
    log = MyLogger()
    log.start_rotate_logging("WorkerLog", os.path.join('', "worker.log"))
    # while True:
    doIter()
        # sleep(10)