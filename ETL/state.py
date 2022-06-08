import abc
import json
from typing import Any, Optional


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        if self.file_path is None:
            raise Exception("File not found")

        with open(self.file_path, "w") as f:
            json.dump(state, f)

    def retrieve_state(self) -> dict:
        if self.file_path is None:
            return {}
        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            self.save_state({})
            return {}


class State:
    """
    Класс для хранения состояния при работе с данным, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределенным хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.state = storage.retrieve_state()

    def set_state(self, key: str, value: any) -> None:
        self.state[key] = value
        self.storage.save_state(self.state)

    def get_state(self, key: str) -> Any:
        return self.state.get(key)
