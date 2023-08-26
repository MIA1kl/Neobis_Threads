FROM python:3.9

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /code

WORKDIR /code

COPY requirements.txt /code/

RUN apt-get update && apt-get install -y libpq-dev python3-dev
RUN pip install -r requirements.txt

COPY . /code/