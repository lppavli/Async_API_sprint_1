from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import BaseModel

from db.elastic import get_elastic
from db.redis import get_redis
from models.data_models import Person, PersonShort

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут
FILM_CACHE_EXPIRE_IN_SECONDS = 60*5


class ListCache(BaseModel):
    __root__: List[str]


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def get_list(self, page_number: int, page_size: int) -> Optional[List[Person]]:
        doc = await self.elastic.search(
            index="persons",
            from_=(page_number - 1) * page_size,
            size=page_size
        )
        return [Person(**d["_source"]) for d in doc["hits"]["hits"]]

    async def search(self, page_number: int, page_size: int, query: str) -> Optional[List[Person]]:
        body = {
                    "query": {
                        "multi_match": {
                            "query": query,
                        }
                    }
                }
        doc = await self.elastic.search(
            index="persons", body=body,
            from_=(page_number - 1) * page_size,
            size=page_size
        )
        return [Person(**d["_source"]) for d in doc["hits"]["hits"]]

    # async def search(self, query: str) -> List[Person]:
    #     body = {
    #         "query": {
    #             "multi_match": {
    #                 "query": query,
    #             }
    #         }
    #     }
    #     persons = await self._get_list_from_elastic(body)
    #     #persons: List[Person] = await self._get_list_from_cache(query)
    #
    #     #if not persons:
    #     #    persons = await self._get_list_from_elastic(body)
    #     #    await self._put_list_to_cache(query, persons)
    #
    #     return persons

    async def _get_list_from_cache(self, cache_key: str) -> Optional[List[Person]]:
        data: str = await self.redis.get(cache_key)

        if not data:
            return None

        data_list: ListCache = ListCache.parse_raw(data)
        persons: list[Person] = [Person.parse_raw(p_data) for p_data in data_list.__root__]
        return persons

    async def _get_list_from_elastic(self, body: dict) -> List[Person]:
        response = self.elastic.search(
            index="persons", body=body,
        )
        return [Person(**d["_source"]) for d in response["hits"]["hits"]]

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get('persons', person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(person.id, person.json(), expire=PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _put_list_to_cache(self, cache_key: str, persons: List[Person]):
        data = [f.json() for f in persons]
        data_row = ListCache.parse_obj(data).json()
        await self.redis.set(cache_key, data_row, expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
