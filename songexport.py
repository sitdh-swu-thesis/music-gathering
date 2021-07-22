import csv, logging

from gathering import engine

def export(dataset, f):
  logging.info('Exporting')
  song_writer = csv.DictWriter(
    f,
    fieldnames=list(dataset[0].keys()),
    dialect=csv.unix_dialect
  )

  logging.info('File dumping...')
  song_writer.writeheader()
  song_writer.writerows(dataset)
  logging.info('Done')

def spotify_export():
  logging.debug('Query records from `Song`')
  from models import Song
  song_listing = Song.query.all()

  songs = []
  logging.info('Formatting data')
  for s in song_listing:
    songs.append({
      'id': s.id,
      'track_id': s.track_id,
      'artist': s.artist,
      'title': s.name,
      'link': s.link,
      'has_lyrics': s.lyrics != None
    })

  with open('export/song-spotify.csv', 'w') as f:
    export(songs, f)

def siamzone_export():
  logging.debug('Query records from `Siamsong`')
  from models import SiamzoneSong
  siamzone_map = SiamzoneSong.query.all()

  siamzone_songs = []
  logging.info('Formatting data')
  for s in siamzone_map:
    siamzone_songs.append({
      'id': s.id,
      'song_id': s.song_id,
      'artist_name': s.artist,
      'title': s.name,
    })

  with open('export/song-siamzone.csv', 'w') as f:
    export(siamzone_songs, f)

def song_mapping_export():
  logging.debug('Query records from `Mapping artist`')
  from models import ArtistMap
  artist_map = ArtistMap.query.filter(ArtistMap.artist_name_siamzone != None).all()

  artists = []
  logging.info('Formatting data')
  for artist in artist_map:
    artists.append({
      'id': artist.id,
      'spotify': artist.artist_name_spotify,
      'siamzone': artist.artist_name_siamzone,
    })

  with open('export/song-mapping.csv', 'w') as f:
    export(artists, f)

def song_exportation():
  song_mapping_export()
  spotify_export()
  siamzone_export()

if __name__ == '__main__':
  song_exportation()