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
    genres: list[GenreForFilm.name] = []
    directors: list[PersonForFilm] = []
    writers: list[PersonForFilm] = []
    actors: list[PersonForFilm] = []


class Person(Base):
    id: str
    name: str
    films: list[FilmForPerson]


class Genre(Base):
    id: str
    name: str
    description: str = ""
