from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.data_models import Genre
from services.genres import GenreService, get_genre_service

router = APIRouter()


@router.get('/{genre_id}', response_model=Genre)
async def genre_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    return Genre(
        id=genre.id,
        name=genre.name,
        description=genre.description
    )