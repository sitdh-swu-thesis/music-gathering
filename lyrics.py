import requests, os, time
from bs4 import BeautifulSoup
from sqlalchemy.orm.query import Query
from models import Song
from gathering import engine

# song_url = 'https://www.musixmatch.com/lyrics/Num-Kala/อีกนานไหม'
# 
# response = requests.get(f'http://localhost:8050/render.html?url={song_url}')
# html = BeautifulSoup(response.text, 'html.parser')
# lyric = html.find('div', class_='lyrics')
# 
# print(response.text)

splash_endpoint = os.environ.get('SPLASH_ENDPOINT')
meemodel_lyrics_endpoint = os.environ.get('MEEMODEL_LYRICS_ENDPOINT')

def query_lyrics(name, artist=None):
  query_url = os.environ.get('MEEMODEL_ENDPOINT')
  p = None
  try:
    p = requests.post(
      query_url,
      data={
        'text': str(name)
      }
    )
  except:
    print('Error----------')
    return None

  bs = BeautifulSoup(p.text, 'html.parser') 
  [result_found] = [s.find('strong') for s in bs.find_all('div', class_='info fz16')]
  if result_found == None:
    print('Song not found:', name)
    return None
  else:
    result_found = result_found.get_text()

  result_found = int(result_found.replace('พบ', '').replace('ผลการค้นหา', '').replace(',', '').strip())
  lyrics_url = None
  print('Result found', result_found, 'song')
  remove_tag = lambda x: x.replace('<a>', '').replace('</a>', '')

  if result_found >= 1:
    for ul in bs.find_all('ul', {'class': 'songlist'}):
      for li in ul.find_all('li'):
        [html_song_name, html_song_artist] = [i for i in str(li).split('> - <')]
        html_song_name = remove_tag(f'{html_song_name}>')
        html_song_artist = remove_tag(f'<{html_song_artist}')

        k_name = BeautifulSoup(html_song_name, 'html.parser').find('a')
        k_artist = BeautifulSoup(html_song_artist, 'html.parser').find('a')

        song_name, song_artist = k_name.text, k_artist.text
        # if 1 == result_found:
        #   lyrics_url = k_name['href']
        #   break
        if song_artist.lower().strip() in artist.lower().strip() or song_artist.lower().strip() == artist.lower().strip():
          print("FOUND", song_name, song_artist) 
          lyrics_url = k_name['href']
          break

  return lyrics_query(lyrics_url) if lyrics_url else None 

def lyrics_query(url):
  lyrics_endpoint = f'{meemodel_lyrics_endpoint}{url}'
  lyrics = None
  try:
    response = requests.get(lyrics_endpoint)

    bs = BeautifulSoup(response.text, 'html.parser')
    lyrics = bs.find('div', {'class': 'lyric', 'id': 'lyric'}).text
  except:
    pass

  return lyrics

def cleanup(song_name):

  if song_name.find(' (') >= 0:
    song_name = song_name[:song_name.find(' (')]
  if song_name.find(' -') >= 0:
    song_name = song_name[:song_name.find(' -')]

  song_name = ''.join([i for i in song_name if i not in ['!', '?', "'"]])
  
  return song_name

def update_lyrics():
  import random
  from sqlalchemy.orm import Session

  with Session(engine) as session:
    songs = session.query(Song).filter(Song.lyrics.is_(None))
    for song in songs:
      if song.lyrics:
        print('Skip for', song.name, 'with lyrics exists')
        continue

      print('Search for:', song.name, 'by', song.artist)
      lyrics = query_lyrics(cleanup(song.name), artist=song.artist)

      if lyrics:
        print('Lyrics found and update')
        song.lyrics = lyrics.strip()
      else:
        song.lyrics = ""
      session.commit()

      print('-' * 10)

      time.sleep(random.random() + random.randint(1, 3))

if __name__ == '__main__':
  update_lyrics()