FROM python:3.12-slim-bookworm AS base

ARG POETRY_VERSION=1.8.4
ARG UID=1000
ARG GID=1000

ENV PYTHONPATH="/app"

RUN groupadd -g ${GID} -o app
RUN useradd -m -d /app -u ${UID} -g ${GID} -o -s /bin/bash app

RUN apt-get update -yqq && apt-get install -yqq --no-install-recommends \
  python3-dev \ 
  build-essential \ 
  pkg-config \
  vim-tiny \
  curl \
  unzip

WORKDIR /app

ENV PYTHONPATH="/app"

CMD ["tail", "-f", "/dev/null"]

FROM base AS poetry

RUN pip install poetry==${POETRY_VERSION}

ENV PYTHONUNBUFFERED=1\
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache

FROM poetry AS build

COPY pyproject.toml poetry.lock README.md ./

RUN poetry export --without dev -f requirements.txt --output requirements.txt

FROM poetry AS development
RUN apt-get update -yqq && apt-get install -yqq --no-install-recommends \
  git

USER app

FROM base AS production

COPY --chown=${UID}:${GID} . /app
COPY --chown=${UID}:${GID} --from=build "/app/requirements.txt" /app/requirements.txt

RUN pip install -r /app/requirements.txt

USER app
