from typing import List, Optional

from .base import Base


class GenreForFilm(Base):
    id: str
    name: str


class PersonForFilm(Base):
    id: str
    name: str


class FilmForPerson(Base):
    id: str
    title: str
    rating: Optional[float]
    type: str


class FilmId(Base):
    id: str


class Film(Base):
    id: str
    title: str
    rating: Optional[float]
    type: str
    description: Optional[str] = ""
    genres: Optional[List[GenreForFilm]]
    directors: Optional[List[PersonForFilm]]
    writers: Optional[List[PersonForFilm]]
    actors: Optional[List[PersonForFilm]]


class Person(Base):
    id: str
    name: str
    films: Optional[List[FilmForPerson]]


class PersonShort(Base):
    id: str
    name: str
    films_ids: Optional[List[FilmId]]


class Genre(Base):
    id: str
    name: str
    description: Optional[str]
