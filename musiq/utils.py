
def new_user_extract(params):
  from datetime import datetime

  return {
    'timestamp': datetime.strptime(params.get('timestamp'), '%m/%d/%Y %H:%M:%S'),
    'email': params.get('email'),
    'consent_accept': 'yes' == params.get('consent_appept'),
    'firstname': params.get('firstname'),
    'lastname': params.get('lastname')
  }

def split_lyric(lyric, splitter=', '):
  lyrics = lyric.split(', ')
  return lyrics if len(lyrics) > 1 else lyric.split("\n")

def format_join(lyrics, glue=',', prefix='', suffix=''):
  longshot = glue.join(lyrics)

  return f"{prefix}{longshot}{suffix}"

def access_key(email, timestamp, recieve_timestamp):
  import os, hashlib, datetime

  h = hashlib.sha256()
  accept_timestamp = int(timestamp.timestamp())
  recieve_timestamp = int(recieve_timestamp.timestamp())
  print(accept_timestamp, '---', recieve_timestamp)

  h.update(f'{accept_timestamp}.{recieve_timestamp}-{email}@{os.getenv("APP_SECRET_KEY")}'.encode())
  serial = h.hexdigest()[:10]

  return f"{serial[:3]}-{serial[3:6]}-{serial[-4:]}".lower()

def prepare_music_list(user, musics):
  from musiq import db
  from models import EmotionMapping
  from datetime import datetime

  process_pass = False

  try:
    mapping_list = [EmotionMapping(user_id=user, song_id=m, created_at=datetime.now()) for m in musics]

    db.session.add_all(mapping_list)
    db.session.commit()

    process_pass = True
  except:
    pass

  return process_pass


def convert_spotify_url(source_url):
  return source_url.replace('com/track', 'com/embed/track')