import enum
import uuid
from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from models.data_models import Film, FilmForPerson
from services.films import FilmService, get_film_service

from fastapi_pagination import Page, add_pagination, paginate


router = APIRouter()


@router.get(
    '/search',
    response_model=Page[FilmForPerson],
)
async def films_search(
        query: str,
        film_service: FilmService = Depends(get_film_service),
):
    """
    Поиск по фильмам
    """
    films = await film_service.search(query)

    return paginate(films)


@router.get('/{film_id}', response_model=Film)
async def film_details(
        film_id: str,
        film_service: FilmService = Depends(get_film_service)
) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return Film(
        id=film.id,
        title=film.title,
        type=film.type,
        imdb_rating=film.rating,
        description=film.description,
        genre=film.genres,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors,
    )


class SortTypes(enum.Enum):
    rating = 'rating'

    def __str__(self) -> str:
        return self.value


@router.get(
    '/',
    response_model=Page[FilmForPerson],
)
async def get_all_films(
        sort: Optional[SortTypes] = None,
        filter: Optional[uuid.UUID] = None,
        film_service: FilmService = Depends(get_film_service),
) -> Page[list[Film]]:

    if not sort:
        sort = ''

    films = await film_service.get_all_films(sort, filter)

    return paginate(films)

add_pagination(router)





