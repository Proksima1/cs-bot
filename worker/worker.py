import argparse
import ftplib
import os
import random
import re
import string
from datetime import datetime, date, timedelta
from time import sleep

from loader import *
from logger import MyLogger


def grabFile(session: ftplib.FTP, filename):
    with open(filename, 'wb') as file:
        session.retrbinary('RETR ' + filename, file.write, 1024)


def placeFile(session: ftplib.FTP, filename):
    session.storbinary('STOR ' + filename, open(filename, 'rb'))


def doIter(start_day: date):
    session = ftplib.FTP(SERVER, USERNAME, PASSWORD)
    download_log(session)
    data = getDiff('cd_logs_prev.log', 'cd_logs.log')
    if len(data) != 0:
        log.add(f'Find difference in file: {data}')
        try:
            os.remove('cd_logs_prev.log')
            os.rename('cd_logs.log', 'cd_logs_prev.log')
            download_vip(session)
            ids = searchForSteamIdInVip(data)
            ids = list(filter(lambda x: not x[1], ids))
            add_steam_ids_to_file(ids, start_day)
            placeFile(session, 'users.ini')
            log.add('Updated VIP on server')
            os.remove('users.ini')
        except Exception as e:
            log.add_error(f'An error has occurred: {e}')
    else:
        log.add(f'No difference found')
    session.close()


def generate_random_name(length):
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string


def count_lines(filename, chunk_size=1 << 13):
    with open(filename, encoding='utf-8', errors='ignore') as file:
        return sum(chunk.count('\n')
                   for chunk in iter(lambda: file.read(chunk_size), '')) + 1


def getDiff(prev: str, curr: str):
    """Checks difference in length between 2 files, creates new one,
    \ containing just a new part, deleting previous file"""
    f = count_lines(prev)
    s = open(curr, 'r+', encoding='utf-8', errors='ignore')
    data = s.readlines()[f:]
    return data


def parse_steam_id(string):
    pattern = r'\[STEAM_(\d+):(\d+):(\d+)\]'
    match = re.search(pattern, string)
    if match:
        steam_id = f'STEAM_{match.group(1)}:{match.group(2)}:{match.group(3)}'
        return steam_id
    else:
        return None


def add_steam_ids_to_file(steam_ids, start_day: date):
    with open('users.ini', 'r', encoding='utf-8', errors='ignore') as f:
        file_content = f.read()
    steam_ids = list(map(lambda x: parse_steam_id(x[0]), steam_ids))
    last_bracket_index = file_content.rfind("}")
    till_time = datetime(start_day.year, start_day.month, start_day.day, 6, 0) + timedelta(days=1)
    timestamp = int(till_time.timestamp())
    steam_id_str = "\n".join([
        f'\t"{sid}"\n\t{{\n\t\t"name"\t\t"{generate_random_name(10)}"\n\t\t"expires"\t\t"{timestamp}"\n\t\t"group"\t\t"GOLD"\n\t}}'
        for sid in steam_ids]) + '\n'
    updated_file_content = file_content[:last_bracket_index] + steam_id_str + file_content[last_bracket_index:]
    with open('users.ini', 'w', encoding='utf-8', errors='ignore') as f:
        f.write(updated_file_content)


def download_log(session):
    session.cwd(LOG_PATH)
    grabFile(session, 'cd_logs.log')


def download_vip(session):
    session.cwd('vip/')
    grabFile(session, 'users.ini')


def searchForSteamIdInVip(steam_ids):
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
    parser = argparse.ArgumentParser(prog='worker')
    parser.add_argument('--start_time', type=int, nargs='?')
    parser.add_argument('--finish_time', type=int, nargs='?')
    start_day = date.today()
    start_time = parser.parse_args().start_time
    log.add(f'Starting with start time {start_time}')
    finish = parser.parse_args().finish_time
    d = datetime.now()
    session = ftplib.FTP(SERVER, USERNAME, PASSWORD)
    download_log(session)
    os.rename('cd_logs.log', 'cd_logs_prev.log')
    while d.time().hour != start_time:
        try:
            download_log(session)
            if os.path.isfile('cd_logs_prev.log'):
                os.remove('cd_logs_prev.log')
            os.rename('cd_logs.log', 'cd_logs_prev.log')
            log.add('Waiting for start time...')
            sleep(60)
            d = datetime.now()
        except Exception as e:
            log.add_error(f'An error has occurred: {e}')
    else:
        session.close()
        if d.time().hour == start_time and d.day == start_day.day:
            d = datetime.now()
            while d.time().hour != 5 or d.time().minute != 58:
                log.add('Starting new iteration')
                doIter(start_day)
                log.add('Iteration done')
                sleep(15)
                d = datetime.now()
            else:
                log.add('Finishing work')
                try:
                    session = ftplib.FTP(SERVER, USERNAME, PASSWORD)
                    session.cwd(LOG_PATH)
                    session.delete('cd_logs.log')
                    log.add('Bye')
                except Exception as e:
                    log.add_error(f'An error has occurred while finishing work: {e}')
