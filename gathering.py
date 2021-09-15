import os, requests, time
from datetime import datetime
from setup import prepare_env
from lxml import html
from sqlalchemy import create_engine
from models import Base

prepare_env()
splash_url_format = os.environ.get('SPLASH_ENDPOINT')

engine = create_engine(
  'postgresql+psycopg2://musiq:musiq@localhost:4444/musiq',
  client_encoding="utf8"
)

def splash_url(url):
  return f'{splash_url_format}={url}'

def get_date_listing():
  spotify_weekly_url = os.environ.get('DOMAIN')
  # weekly_listing_path = '//*[@id="content"]/div/div/div/span/div[1]/div/div/div/div[3]/ul/li'
  weekly_listing_path = '//*[@id="content"]/div/div/div/span/div[1]/div/div/div/div[3]/ul//li/@data-value'

  response = requests.get(splash_url(spotify_weekly_url))
  tree = html.fromstring(response.content)
  weekly = tree.xpath(weekly_listing_path)

  weekly_index = {}
  for l in [w for w in weekly if int(w[:4]) >= 2017]:
    k, _ = l.split('--')
    weekly_index[k] = l.strip()
  
  return weekly_index

def url_formator(weekly_set):
  endpoint_url = os.environ.get('DOMAIN')

  weekly = {}
  for i, w in weekly_set.items():
    weekly[i] = f'{endpoint_url}/{w}'

  weekly = {i: f'{endpoint_url}/{w}' for i, w in weekly_set.items()}

  return weekly

def song_listing(weekly):
  extract_song_path = '//*[@id="content"]/div/div/div/span/table/tbody/tr'

  for wk_string, url in weekly.items():
    print('Getting url:', url)
    wk = datetime.strptime(wk_string, '%Y-%m-%d').date()
    response = requests.get(splash_url(url))

    song_listing = html.fromstring(response.content)
    weekly_song = song_listing.xpath(extract_song_path)

    weekly_song_info = []

    for w in weekly_song:
      # Image Cover
      [cover_image] = w.xpath('td[@class="chart-table-image"]/a/img/@src')
      # Song link
      [song_link] = w.xpath('td[@class="chart-table-image"]/a/@href')
      [weekly_position] = w.xpath('td[@class="chart-table-position"]/text()')
      [song_name] = w.xpath('td[@class="chart-table-track"]/strong/text()')
      [song_artist] = w.xpath('td[@class="chart-table-track"]/span/text()')
      song_artist = song_artist[3:]
      [streaming_number] = w.xpath('td[@class="chart-table-streams"]/text()')
      streaming_number = int(streaming_number.replace(',', ''))
      track_id = song_link.split('/')[-1]

      weekly_song_info.append({
        'track_id': track_id,
        'cover_image': cover_image,
        'song_link': song_link,
        'position': int(weekly_position),
        'name': song_name,
        'artist': song_artist,
        'streaming_number': streaming_number,
      })

    store_song_info(wk, week_key=wk_string, song_list=weekly_song_info)
    print('Ending', wk_string)
    print('Sleeping for', 0.5, 'sec')
    print()
    time.sleep(0.5)

def store_song_info(week, week_key=None, song_list=None):
  from sqlalchemy.orm import Session
  from models import WeeklyStats, Song

  with Session(engine) as session:
    for song in song_list:
      s = None
      s = session.query(Song).filter(Song.track_id == song['track_id']).first()
      if s == None:
        s_info = Song(
          track_id = song['track_id'],
          artist = song['artist'],
          name = song['name'],
          cover_image = song['cover_image'],
          link = song['song_link']
        )

        try:
          session.add(s_info)
          session.commit()
          s = s_info
        except:
          pass

      w = WeeklyStats(
        week_id = week.strftime('%Y-%m-%d'),
        week_date = week,
        position = song['position'],
        song = s.id,
        name = song['name'],
        artist = song['artist'],
        streaming_count = song['streaming_number']
      )
      session.add(w)

    session.commit()

def db_preparation():
  from models import Base
  Base.metadata.create_all(engine)

def main_gathering():
  db_preparation()
  # dataset = get_date_listing()
  # url_format = url_formator(dataset)
  # song_listing(url_format)

if __name__ == '__main__':
  main_gathering()