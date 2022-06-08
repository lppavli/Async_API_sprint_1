import orjson

from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Base(BaseModel):
    """Base class for all models API"""

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
