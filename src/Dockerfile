FROM python:3.8.0-alpine3.10

COPY ./requirements.txt .
RUN apk update \
    && apk add build-base
RUN pip install -U setuptools pip
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8080

WORKDIR /app

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]