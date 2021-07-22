import json
import os
from flask import Flask, render_template, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from requests import models

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
  SECRET_KEY='dev'
)

if os.path.isfile('config.cfg'):
  pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://musiq:musiq@localhost:5555/musiq'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

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

  with open('song_table.json', 'w') as f:
    import json
    app.logger.debug('Dump data to file')
    json.dump(song_info, f)
    app.logger.debug('Done')

if not os.path.isfile('song_table.json'):
  app.logger.debug('song_table.json file not found')
  export_siamzone_artist()

@app.route("/")
def index():
  songs = []
  with open('song_table.json') as f:
    import json
    songs = json.load(f)
    
  return render_template('index.html', songs=songs)

@app.route('/api/artist/next')
def next_artist():
  from models import ArtistMap, Song
  artist_list = [a.artist_name_spotify.strip() for a in ArtistMap.query.with_entities(ArtistMap.artist_name_spotify).distinct()]

  song_artist = [a.artist for a in Song.query.filter(~Song.artist.in_(artist_list)).limit(1)]
  return make_response(jsonify({
    'artist': None if 0 == len(song_artist) else song_artist[0],
  }), 200)

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