from pathlib import Path
import enum
import functools

from sqlalchemy import create_engine, Enum, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker
import sqlalchemy

Base = declarative_base()

Column = functools.partial(sqlalchemy.Column, nullable=False)


class ContentType(enum.Enum):
    MOVIES = 1
    TV = 2

    @classmethod
    def from_str(cls, s):
        s = s.lower()
        if s == "movies":
            return ContentType.MOVIES
        elif s == "tv":
            return ContentType.TV
        else:
            raise ValueError


class Root(Base):
    __tablename__ = 'roots'

    id = Column(Integer, primary_key=True)
    path = Column(String)
    content_type = Column(Enum(ContentType))


class Subtitle(Base):
    __tablename__ = 'subtitles'

    id = Column(Integer, primary_key=True)
    lang = Column(String(3), nullable=True)  # alpha_3 code

    movie_id = Column(Integer, ForeignKey('movies.id'))
    movie = relationship('Movie', backref=backref('subtitles', cascade="delete"))

    file_id = Column(Integer, ForeignKey('files.id'))
    file = relationship('File', cascade="delete")


class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    original_title = Column(String)
    year = Column(Integer)
    overview = Column(String)
    tmdb_id = Column(Integer, unique=True)

    file_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    file = relationship('File', foreign_keys=[file_id], cascade='delete')

    poster_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    poster = relationship('File', foreign_keys=[poster_id], cascade='delete')

    backdrop_id = Column(Integer, ForeignKey('files.id'), nullable=True)
    backdrop = relationship('File', foreign_keys=[backdrop_id], cascade='delete')


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    path = Column(String)  # relative to the root

    root_id = Column(Integer, ForeignKey('roots.id'))
    root = relationship('Root', foreign_keys=[root_id], backref=backref(
        "files", cascade="delete"), lazy='immediate')

    def get_abspath(self):
        return Path(self.root.path) / self.path

    def get_path(self):
        return Path(self.path)

    def set_path(self, path, relative_to=None):
        if relative_to is None:
            self.path = str(path)
        elif isinstance(relative_to, (str, Path)):
            self.path = str(Path(path).relative_to(relative_to))
        elif isinstance(relative_to, Root):
            self.path = str(Path(path).relative_to(relative_to.path))
        else:
            raise ValueError('relative_to has an invalid value')


import os  # noqa
# os.unlink('library.db')
_engine = create_engine('sqlite:///library.db')
Base.metadata.create_all(_engine)
Session = sessionmaker(bind=_engine)
