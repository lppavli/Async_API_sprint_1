## Проект Асинхронное API

https://github.com/lppavli/Async_API_sprint_1
## Используемые технологии
- Код приложения пишется на Python + FastAPI.
- Приложение запускается под управлением сервера ASGI(uvicorn).
- Хранилище – ElasticSearch.
- За кеширование данных отвечает – redis cluster.
- Все компоненты системы запускаются через docker.
## Назначение и имена контейнеров в docker-compose
- postgres - база данных postgresql
- redis - redis
- etl - процесс ETL для загрузки данных из postgres в elasticsearch
- async-api - модуль FastAPI
- nginx - сервер nginx, который отдает это все во внешний мир
## Для запуска проекта необходимо
- Создать в папках ETL, src и в корневой папке проекта файл .env следующего содержимого:
~~~
DB_NAME=movies_database
DB_USER=app
DB_PASSWORD=123qwe
DB_HOST=host
DB_PORT=port
SECRET_KEY=secret
REDIS_HOST=host
REDIS_PORT=port
ELASTIC_HOST=host
ELASTIC_PORT=port
~~~
- Собрать приложение, используя команду docker-compose build
- Запустить, используя команду docker-compose up

