import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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