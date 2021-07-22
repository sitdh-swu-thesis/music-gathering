from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base

from musiq import db

Base = declarative_base()

class Datetime(Base):
  __tablename__ = 'datetime'

  id = Column(Integer, primary_key=True)
  week_date = Column(Date)
  day = Column(Integer)
  month = Column(Integer)
  year = Column(Integer)
  month_name = Column(String)

class Config(Base):
  __tablename__ = 'config'
  id = Column(Integer, primary_key=True, autoincrement=True)
  name = Column(String(50))
  value = Column(Text)

class Song(Base, db.Model):
  __tablename__ = 'song'

  id = Column(Integer, primary_key=True, autoincrement=True)
  track_id = Column(String)
  artist = Column(String)
  name = Column(String)
  cover_image = Column(String)
  link = Column(String)
  lyrics = Column(Text, nullable=True)
  language = Column(String(10), nullable=True)

class SiamzoneSong(Base, db.Model):
  __tablename__ = 'siamzone_song'

  id = Column(Integer, primary_key=True, autoincrement=True)
  song_id = Column(Integer)
  artist = Column(String)
  artist_english = Column(String)
  name = Column(String)
  lyrics = Column(Text, nullable=True)
  language = Column(String(10), nullable=True)


class WeeklyStats(Base, db.Model):
  __tablename__ = 'weekly_stats'
  id = Column(Integer, primary_key=True, autoincrement=True)
  week_id = Column(String)
  week_date = Column(Date)
  position = Column(Integer)

  song = Column(Integer, nullable=True)
  # Song name
  name = Column(String)
  artist = Column(String)
  streaming_count = Column(Integer)

class ArtistMap(Base, db.Model):
  __tablename__ = 'artist_map'
  id = Column(Integer, primary_key=True, autoincrement=True)
  artist_name_spotify = Column(String)
  artist_name_siamzone = Column(String)
