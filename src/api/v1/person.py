from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from models.data_models import Person
from services.persons import PersonService, get_person_service

router = APIRouter()


@router.get('/{person_id}', response_model=Person)
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return Person(
        id=person.id,
        name=person.name,
        films=person.films
    )

@router.get('/search')
async def person_list(page_size: int, page_number: int,
                      person_service: PersonService = Depends(get_person_service)):
    persons = await person_service.get_list(page_number, page_size)
    return persons


@router.get('/{person_id}/film/', response_model=Person)
async def person_list(person_id: str, person_service: PersonService = Depends(get_person_service)) -> None:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return person.films
