from pydantic import BaseModel


class CacheValue(BaseModel):
    name: str
    value: str


class ServiceMixin:
    _index_name: str

    def _build_cache_key(self, cache_values: list[CacheValue]) -> str:
        separate = ':'
        key = f'{self._index_name}{separate}'
        for v in cache_values:
            key += f'{v.name}{separate}{v.value}'

        return key