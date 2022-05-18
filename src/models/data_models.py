from typing import List

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


class Film(FilmForPerson):
    description: str = ""
    genres: List[GenreForFilm] = []
    directors = List[PersonForFilm] = []
    writers = List[PersonForFilm] = []
    actors = List[PersonForFilm] = []


class Person(PersonForFilm):
    films: List


class Genre(GenreForFilm):
    description: str = ""
