# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100
WORKDIR /code
RUN pip install poetry
RUN apt update
RUN apt install python3-setuptools -y
COPY poetry.lock pyproject.toml /code/
RUN poetry config virtualenvs.create false \
  && poetry update && poetry install --no-interaction --no-ansi
COPY . /code/