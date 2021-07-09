import requests, time
from lxml import html
from gathering import db_preparation

def siamzone_scrap(start = 1, stop = 1):
  from sqlalchemy.orm import Session
  from models import SiamzoneSong
  from gathering import engine

  siamzone_url = 'https://www.siamzone.com/music/thailyric'
  song_info_xpath = "//div[contains(@class, 'has-text-grey') and contains(@class, 'is-size-7')]//a/text()"
  lyric_xpath = "//div[contains(@class, 'columns') and contains(@class, 'is-variable') and contains(@class, 'is-3')]//div[contains(@class, 'has-text-centered-mobile') and contains(@class, 'is-size-5-desktop')]//div[position()=1]/text()"

  stop = start if start >= stop else stop

  with Session(engine) as session:
    for i in range(start, stop + 1):
      response = requests.get(f'{siamzone_url}/{i}')
      tree = html.fromstring(response.content)
      [title] = tree.xpath('//title/text()')
      song_title, artist = None, None

      try:
        song_title, artist = [c.strip() for c in title.replace('เนื้อเพลง', '').split('|')]
      except:
        continue


      song_info = tree.xpath(song_info_xpath)
      if 2 == len(song_info):
        [artist_name, _] = [c.strip() for c in song_info]
      else:
        artist_name = song_info[0].strip()

      artist_name_en = None
      if '(' in artist_name:
        artist_name_en = artist_name.strip()[artist_name.index('(')+1:-1].strip()

      lyric_body = "\n".join([c.strip() for c in tree.xpath(lyric_xpath) if len(c.strip()) > 0])
      
      song = SiamzoneSong(
        song_id = i,
        name = song_title,
        artist = artist_name,
        artist_english = artist_name_en,
        lyrics = lyric_body
      )
      session.add(song)

      session.commit()
      print(i, ':', song_title, 'by', artist)
      time.sleep(1)

if __name__ == '__main__':
  db_preparation()
  siamzone_scrap(start=20915, stop=21419)
