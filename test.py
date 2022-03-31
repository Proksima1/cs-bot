import requests
from bs4 import BeautifulSoup

"""STEAM_0:1:577154573"""
resp = requests.post('https://steamid.io/lookup', data={'input': '1'})
soup = BeautifulSoup(resp.text, 'html.parser')
steam_id = soup.find('dl', class_='panel-body').find_all('dd', class_='value')[0].find('a').text