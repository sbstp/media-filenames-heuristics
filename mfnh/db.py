from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Subtitle(Base):
    __tablename__ = 'subtitles'

    id = Column(Integer, primary_key=True)
    lang = Column(String(3), nullable=True)  # alpha_3 code

    # movie
    movie_id = Column(String, ForeignKey('movies.id'))

    # file
    file = relationship('File')
    file_id = Column(Integer, ForeignKey('files.id'))


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    original_title = Column(String)
    year = Column(Integer)
    overview = Column(String)
    tmdb_id = Column(Integer, unique=True)
    # file
    file_id = Column(Integer, ForeignKey('files.id'))
    file = relationship('File', foreign_keys=[file_id], cascade='delete')
    # subtitles
    subtitles = relationship('Subtitle', backref="movie", cascade='delete')
    # poster
    poster_id = Column(Integer, ForeignKey('files.id'))
    poster = relationship('File', foreign_keys=[poster_id], cascade='delete')
    # poster
    backdrop_id = Column(Integer, ForeignKey('files.id'), )
    backdrop = relationship('File', foreign_keys=[backdrop_id], cascade='delete')


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    path = Column(String)  # relative path from the root
    original_path = Column(String)


import os  # noqa
# os.unlink('library.db')
_engine = create_engine('sqlite:///library.db')
Base.metadata.create_all(_engine)
Session = sessionmaker(bind=_engine)
