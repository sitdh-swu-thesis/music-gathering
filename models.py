from datetime import datetime
from enum import auto
from sqlalchemy import Column, Integer, String, Date, Text, DateTime, BigInteger, ForeignKey
from sqlalchemy.orm import relation, relationship
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

class User(Base, db.Model):
  __tablename__ = 'user'

  id = Column(Integer, primary_key=True, autoincrement=True)
  username = Column(String)
  email = Column(String, unique=True)
  access_token = Column(String)
  created_at = Column(DateTime)
  updated_at = Column(DateTime, default=datetime.utcnow)

class AccessLog(Base, db.Model):
  __tablename__ = 'access_log'

  id = Column(Integer, primary_key=True, autoincrement=True)
  access_date = Column(DateTime, default=datetime.utcnow)
  user_id = Column(Integer, ForeignKey('user.id')) 
  user = relationship('User', back_populates='access_log') 

User.access_log = relationship('AccessLog', order_by=AccessLog.id, back_populates='user')

class Emotion(Base, db.Model):
  __tablename__ = 'emotion'

  id = Column(Integer, primary_key=True, autoincrement=True)
  emotion_title = Column(String)

class EmotionMapping(Base, db.Model):
  __tablename__ = 'emotion_mapping'

  id = Column(BigInteger, primary_key=True, autoincrement=True)
  user_id = Column(Integer, ForeignKey('user.id'))
  user = relationship('User', backref='emotion_mapping')

  song_id = Column(Integer, ForeignKey('song.id'))
  song = relationship('Song', backref='emotion_mapping')

  emotion_id = Column(Integer, ForeignKey('emotion.id'))
  emotion = relationship('Emotion', back_populates='emotion_mapping')

  created_at = Column(DateTime)
  updated_at = Column(DateTime, default=datetime.utcnow)

Emotion.emotion_mapping = relationship('EmotionMapping', order_by=EmotionMapping.id, back_populates='emotion')