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
    rating: float = None
    type: str


class Film(Base):
    id: str
    title: str
    rating: float = None
    type: str
    description: str = ""
    genres: Optional[List[GenreForFilm]]
    directors = Optional[list[PersonForFilm]]
    writers = Optional[list[PersonForFilm]]
    actors = Optional[list[PersonForFilm]]


class Person(Base):
    id: str
    name: str
    films: Optional[list[FilmForPerson]]


class Genre(Base):
    id: str
    name: str
    description: str = ""
