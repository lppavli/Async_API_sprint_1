import uuid
from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.data_models import Film, FilmForPerson

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_all_films(
            self,
            sort: Optional[str],
            filter: Optional[str] = None,
    ) -> list[FilmForPerson]:

        body = {
            "query": {
                'match_all': {}
            }
        }

        if sort:
            body['sort'] = [
                {
                    f"{sort}": "desc"
                },
                "_score"
            ]

        films = await self._search_films(body)
        return films

    async def search(self, query: str) -> list[FilmForPerson]:
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fuzziness": "auto",
                    "fields": [
                        "actors_names",
                        "writers_names",
                        "title",
                        "description",
                        "genre"
                    ]
                }
            }
        }
        films = await self._search_films(body)

        return films

    async def _search_films(self, body: dict) -> list[FilmForPerson]:

        response = await self.elastic.search(
            index='movies',
            body=body,
        )
        return self._convert_to_model(response)

    @staticmethod
    def _convert_to_model(response: dict) -> list[FilmForPerson]:
        return [FilmForPerson(**d['_source']) for d in response['hits']['hits']]

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None
        film = Film.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
