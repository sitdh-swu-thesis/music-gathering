# from gathering import song_listing
from musiq.utils import prepare_music_list
import os, logging
from flask import Flask, render_template, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from requests import models

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
  SECRET_KEY='dev'
)

if os.path.isfile('config.cfg'):
  pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://musiq:musiq@localhost:4444/musiq'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

def all_musics():
  import random

  from sqlalchemy import and_
  from models import Song

  songs = [s.id for s in Song.query.filter(
    Song.language == 'TH',
    Song.lyrics != None
  ).all()]

  for _ in range(1, random.randint(3, 11)):
    random.shuffle(songs)

  return songs

def export_siamzone_artist():
  from models import SiamzoneSong

  app.logger.debug('Prepare for song table')

  songs = SiamzoneSong.query.limit(10).all()
  song_info = []
  for song in songs:
    app.logger.debug(song.artist)
    song_info.append({
      'id': song.id,
      'title': song.name,
      'artist': song.artist,
      'artist_en': song.artist_english
    })

  app.logger.debug('Data serialized')

  l = len(song_info)
  app.logger.debug(f'Data found {len(song_info)} record(s)')

@app.route("/")
def index():
  return render_template('index.html')

@app.route('/api/artist/next')
def next_artist():
  from models import ArtistMap, Song
  artist_list = [a.artist_name_spotify.strip() for a in ArtistMap.query.with_entities(ArtistMap.artist_name_spotify).distinct()]

  song_artist = [a.artist for a in Song.query.filter(~Song.artist.in_(artist_list)).limit(1)]
  return make_response(jsonify({
    'artist': None if 0 == len(song_artist) else song_artist[0],
  }), 200)

@app.route('/api/thai/song')
def next_song():
  from models import Song
  s = [s for s in Song.query.filter(
      Song.lyrics == None,
      Song.language == 'TH'
    ).limit(1)]
  status_code = 404
  if len(s):
    s = s[0]
    s = {
      'track_id': s.track_id,
      'artist': s.artist,
      'name': s.name,
    }
    status_code = 200
  else:
    s = None

  return make_response(jsonify({
    'song': s if s else None
  }), status_code)

  # song_artist = [a.artist for a in Song.query.filter(~Song.artist.in_(artist_list)).limit(1)]
  # return make_response(jsonify({
  #   'artist': None if 0 == len(song_artist) else song_artist[0],
  # }), 200)

@app.route('/api/song/search/<string:q>')
def search_song(q):
  from models import SiamzoneSong

  songs = []
  songs_results = SiamzoneSong.query.with_entities(SiamzoneSong.artist, SiamzoneSong.name, SiamzoneSong.lyrics).distinct().filter(SiamzoneSong.name.like(f'%{q}%'))
  for song in songs_results:
    songs.append({
      'artist': song.artist,
      'name': song.name,
      'lyric': song.lyrics,
    })

  return make_response(
    jsonify(songs),
    200 if len(songs) > 0 else 404
  )


@app.route('/api/artist/search/<string:q>')
def search_artist(q):
  from models import SiamzoneSong, Song

  artist_result = SiamzoneSong.query.with_entities(SiamzoneSong.artist, SiamzoneSong.artist_english).distinct().filter(SiamzoneSong.artist.like(f'%{q}%'))
  app.logger.debug(artist_result)
  artists = []
  for a in artist_result:
    artists.append({
      'artist_thai': a.artist,
      'artist_english': a.artist_english,
    })

  return make_response(
    jsonify(artists),
    200 if len(artists) > 0 else 404
  )

@app.route('/api/song/lyric/update', methods=['POST'])
def update_song_lyric():
  from flask import request
  from models import Song

  content = request.json

  num_rows = Song.query.filter(Song.track_id == content.get('track_id')).update({
    'lyrics': content.get('lyric')
  })
  db.session.commit()

  return make_response(
    jsonify({
      'update_row': num_rows
    }),
    201 if num_rows else 200
  )

@app.route('/api/map/artist', methods=['POST'])
def map_artist():
  from flask import request
  from models import ArtistMap

  content = request.json

  spotify_artist = content.get('spotify_artist')
  known_artists = content.get('mapped_artists')

  if 0 == len(known_artists):
    app.logger.debug(f'Empty artist for {spotify_artist}')
    db.session.add(ArtistMap(
      artist_name_spotify=spotify_artist,
      artist_name_siamzone=None
    ))

  else:
    app.logger.debug(f'Updating list of artist for {spotify_artist}')
    for artist in known_artists:
      db.session.add(ArtistMap(
        artist_name_spotify=spotify_artist,
        artist_name_siamzone=artist
      ))

  db.session.commit()

  return make_response(jsonify(content), 200)

# /********************
# / Emotion
# /********************

# View 
# - - -
# Display form
@app.route("/lyric/<string:access_token>")
def lyric(access_token):
  return render_template('lyric.html')

# API
# - - -
# Create user 

@app.route('/api/user/new', methods=['POST'])
def user_create_new_user():
  from flask import request
  from datetime import datetime
  from musiq.utils import new_user_extract, access_key

  from models import User
  import string, random, datetime

  '''
    - timestamp: "m/d/yyyy H:M:s" -> "9/15/2021 20:38:45"
    - email: hello@example.com
    - consent_accept: yes, no
    - firstname: john
    - lastname: doe
  '''
  user_info = new_user_extract(request.json)
  app_datetime = datetime.datetime.utcnow()

  user_access_key = access_key(
    user_info['email'],
    user_info.get('timestamp'),
    app_datetime
  )

  status_code = 400
  response_message = {
    'code': 4000,
    'name': 'Invalid email',
    'describtion': 'Check email and try again',
  }


  try:
    user = User(
      username=user_info['email'],
      email=user_info['email'],
      access_token=user_access_key,
      created_at=user_info.get('timestamp'),
      updated_at=app_datetime,
    )

    db.session.add(user)
    db.session.commit()

    prepare_music_list(
      user.id, all_musics()
    )

    response_message = {
      'custom_endpoint': f'https://arokaya.fin/lyric/{user_access_key}' ,
    }

    status_code = 201
    logging.info('Create new user')
  except:
    pass

  return make_response(
    jsonify(response_message),
    status_code
  )


@app.route('/api/emotion/map/next', methods=['GET'])
def mapping_emotion_next_song():

  return make_response(jsonify({
    'track_id': 1238,
    'source': 'https://open.spotify.com/embed/track/5JoSLllHkOdE56kpHU4fi6',
    'artist': 'Pramote Vilepana',
    'title': 'คืนที่ดาวเต็มฟ้า',
    'lyric': '<div class="row justify-content-md-center">' + \
      '</div><div class="row justify-content-md-center">'.join('ปล่อยให้ใจ เข้าข้างตัวเองทุกที, ว่าจะมี เธออยู่กับฉัน, แม้วันนี้ จะยังไม่มีวันนั้น, ก็จะฝัน จะเฝ้ารอ'.split(', ')) + \
      "</div>", 
  }), 200)

@app.route('/api/test', methods=['GET'])
def api_test():
  from models import User
  u = User.query.filter(User.access_token == 'abcd').limit(1)

  e = 'Empty' if u else 'Found'

  return make_response(jsonify({
    'result': e,
  }), 200)

  