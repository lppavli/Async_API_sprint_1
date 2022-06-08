from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.data_models import Genre
from services.genres import GenreService, get_genre_service

router = APIRouter()


@router.get("/{genre_id}", response_model=Genre, description="Вывод информации о жанре")
async def genre_details(
    genre_id: str, genre_service: GenreService = Depends(get_genre_service)
) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return Genre(id=genre.id, name=genre.name, description=genre.description)


@router.get("/", description="Вывод списка жанров")
async def genre_list(
    page_size: int,
    page_number: int,
    genre_service: GenreService = Depends(get_genre_service),
):
    genres = await genre_service.get_list(page_number, page_size)
    return genres
