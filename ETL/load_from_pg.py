import logging
import os
from time import sleep

import backoff
import psycopg2
from dotenv import load_dotenv
from elasticsearch import Elasticsearch, ElasticsearchException
from psycopg2.extras import DictCursor

from queries import FW_QUERY, GENRE_QUERY, PERSON_QUERY, counts
from state import JsonFileStorage, State
from urllib3.exceptions import HTTPError

logging.basicConfig(level=logging.INFO)
load_dotenv()
BATCH_SIZE = 100


class Extraction:
    def __init__(self, conn, query_db) -> None:
        self.cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.query = query_db

    @backoff.on_exception(
        wait_gen=backoff.expo, exception=(psycopg2.Error, psycopg2.OperationalError)
    )
    def extract(self, modified):
        self.cursor.execute(self.query % tuple([modified] * counts[self.query]))
        logging.info("Data extracted.")
        while batch := self.cursor.fetchmany(BATCH_SIZE):
            yield from batch


class Transform:
    def __init__(self, conn, ind, data_l) -> None:
        self.data = data_l
        self.index = ind
        self.cursor = conn.cursor()

    def transform(self):
        res = {}
        d = self.data
        if self.index == "movies":
            directors = [
                {"id": el["person_id"], "name": el["person_name"]}
                for el in d["persons"]
                if el["person_role"] == "director"
            ]
            writers = [
                {"id": el["person_id"], "name": el["person_name"]}
                for el in d["persons"]
                if el["person_role"] == "writer"
            ]
            actors = [
                {"id": el["person_id"], "name": el["person_name"]}
                for el in d["persons"]
                if el["person_role"] == "actor"
            ]
            genres = [{"id": el["g_id"], "name": el["g_name"]} for el in d["genres"]]
            res = {
                "id": d["id"],
                "title": d["title"],
                "description": d["description"],
                "type": d["type"],
                "creation_date": d["created"],
                "rating": d["rating"],
                "modified": d["modified"],
                "directors": directors,
                "writers": writers,
                "actors": actors,
                "genres": genres,
            }
        elif self.index == "genres":
            res = {
                "id": d["genre_id"],
                "name": d["genre_name"],
                "description": d["genre_description"],
                "modified": d["modified"],
            }
        elif self.index == "persons":
            roles = ", ".join(d["roles"])
            films = [
                {
                    "id": el["fw_id"],
                    "rating": el["fw_rating"],
                    "title": el["fw_title"],
                    "type": "fw_type",
                }
                for el in d["films"]
            ]
            res = {
                "id": d["id"],
                "name": d["full_name"],
                "modified": d["modified"],
                "roles": roles,
                "films": films,
            }
        return res


class Load:
    def __init__(self, conn, ind, data_from_t) -> None:
        self.data = data_from_t
        self.index = ind
        self.cursor = conn.cursor()
        host = os.getenv("ELASTIC_HOST", "localhost")
        port = os.getenv("ELASTIC_PORT", "9200")
        self.es = Elasticsearch(f"{host}:{port}")

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(ElasticsearchException, HTTPError),
        max_tries=10,
    )
    def load_data(self):
        self.es.index(
            index=self.index, id=self.data["id"], body=self.data, doc_type="_doc"
        )
        logging.info("Data loaded.")


@backoff.on_exception(
    wait_gen=backoff.expo,
    exception=psycopg2.OperationalError,
    max_tries=5,
)
def main():
    state = State(JsonFileStorage("state.json"))
    dsl = {
        "dbname": os.getenv("DB_NAME", "movies_database"),
        "user": os.getenv("DB_USER", "app"),
        "password": os.getenv("DB_PASSWORD", "123qwe"),
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", 5432),
    }
    queries = {"genres": GENRE_QUERY, "persons": PERSON_QUERY, "movies": FW_QUERY}
    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        logging.info("PostgreSQL connection is open. Start load movies data.")
        while True:
            for index, query in queries.items():
                e = Extraction(pg_conn, query)
                state_key = f"{index}_modified"
                last_modified = state.get_state(state_key)
                for data in e.extract(last_modified):
                    data_t = Transform(pg_conn, index, data).transform()
                    Load(pg_conn, index, data_t).load_data()
                    state.set_state(state_key, data_t["modified"].isoformat())
            sleep(1)


if __name__ == "__main__":
    main()
