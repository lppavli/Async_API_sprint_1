FROM python:3.9.12-alpine3.14

RUN apk update \
    && apk add build-base


COPY ./requirements.txt .


RUN pip install -U setuptools pip
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

WORKDIR /app

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "main:app"]