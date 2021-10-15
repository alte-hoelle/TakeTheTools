# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100
WORKDIR /code
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python - --preview
ENV PATH "/root/.local/bin:$PATH"
COPY poetry.lock pyproject.toml /code/
RUN poetry config virtualenvs.create false
ENV CURL_CA_BUNDLE=""
RUN poetry install --no-interaction --no-ansi
RUN pip install requests