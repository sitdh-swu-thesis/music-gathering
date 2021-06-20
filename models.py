from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.ext.declarative import declarative_base

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

class Song(Base):
  __tablename__ = 'song'

  id = Column(Integer, primary_key=True, autoincrement=True)
  track_id = Column(String)
  artist = Column(String)
  name = Column(String)
  cover_image = Column(String)
  link = Column(String)
  lyrics = Column(Text, nullable=True)

class WeeklyStats(Base):
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