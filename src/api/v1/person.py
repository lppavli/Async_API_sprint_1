from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from models.data_models import PersonShort, FilmId
from services.persons import PersonService, get_person_service

router = APIRouter()


@router.get(
    "/{person_id}",
    response_model=PersonShort,
    description='Описание персоны'
)
async def person_details(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> PersonShort:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")

    return PersonShort(
        id=person.id,
        name=person.name,
        films_ids=[FilmId(id=f.id) for f in person.films],
    )


@router.get(
    "/",
    description='Вывод всех персон'
)
async def person_list(
    page_size: int,
    page_number: int,
    person_service: PersonService = Depends(get_person_service),
) -> Optional[List[PersonShort]]:
    persons = await person_service.get_list(page_number, page_size)
    return [
        PersonShort(id=p.id, name=p.name, films_ids=[FilmId(id=f.id) for f in p.films])
        for p in persons
    ]


@router.get(
    "/search/",
    description='Поиск по персонам'
)
async def person_search(
    query: str,
    page_size: int,
    page_number: int,
    person_service: PersonService = Depends(get_person_service),
) -> Optional[List[PersonShort]]:
    persons = await person_service.search(page_number, page_size, query)
    return [
        PersonShort(id=p.id, name=p.name, films_ids=[FilmId(id=f.id) for f in p.films])
        for p in persons
    ]


@router.get(
    "/{person_id}/film/",
    description='Вывод фильмов по персоне'
)
async def person_list_films(
    person_id: str, person_service: PersonService = Depends(get_person_service)
) -> Optional[List]:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person.films
