from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.data_models import Genre
from services.tools import CacheValue, ServiceMixin


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService(ServiceMixin):
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self._index_name = 'genres'

    async def get_by_id(self, genre_id: str) -> Optional[Genre]:

        cache_key = self._build_cache_key(
            [CacheValue(name='genre_id', value=genre_id)]
        )
        genre = await self._genre_from_cache(cache_key)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(cache_key, genre)
        return genre

    async def get_list(self, page_number: int, page_size: int):
        doc = await self.elastic.search(
            index=self._index_name, from_=(page_number - 1) * page_size, size=page_size
        )
        return [Genre(**d["_source"]) for d in doc["hits"]["hits"]]

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(self._index_name, genre_id)
        except NotFoundError:
            return None
        return Genre(**doc["_source"])

    async def _genre_from_cache(self, genre_id: str) -> Optional[Genre]:
        data = await self.redis.get(genre_id)
        if not data:
            return None
        genre = Genre.parse_raw(data)
        return genre

    async def _put_genre_to_cache(self, cache_key: str, genre: Genre):
        await self.redis.set(
            cache_key, genre.json(), expire=GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
