import requests
from bs4 import BeautifulSoup

song_url = 'https://www.musixmatch.com/lyrics/Num-Kala/อีกนานไหม'

response = requests.get(f'http://localhost:8050/render.html?url={song_url}')
html = BeautifulSoup(response.text, 'html.parser')
lyric = html.find('div', class_='lyrics')

print(response.text)