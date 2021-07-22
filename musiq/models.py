from sqlalchemy import Column, Integer, String, Date, Text
from musiq import db

class SiamzoneSong(db.Model):
  __tablename__ = 'siamzone_song'

  id = Column(Integer, primary_key=True, autoincrement=True)
  song_id = Column(Integer)
  artist = Column(String)
  artist_english = Column(String)
  name = Column(String)
  lyrics = Column(Text, nullable=True)
  language = Column(String(10), nullable=True)