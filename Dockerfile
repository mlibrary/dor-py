# PYTHON image
# Use the official Docker Python image because it has the absolute latest bugfix version of Python
# it has the absolute latest system packages
# it’s based on Debian Bookworm (Debian 12), released June 2023
# Initial Image size is 51MB
# At the end Image size is 156MB

# I did not recommed using an alpine image because it lacks the package installer pip and the support for installing
# wheel packages, which are both needed for installing applications like Pandas and Numpy.

# The base layer will contain the dependencies shared by the other layers
FROM python:3.12-slim-bookworm AS base

# Allowing the argumenets to be read into the dockerfile. Ex:  .env > compose.yml > Dockerfile
ARG POETRY_VERSION=1.8.4
ARG UID=1000
ARG GID=1000

ENV PYTHONPATH="/app"

# Create our users here in the last layer or else it will be lost in the previous discarded layers
# Create a system group named "app_user" with the -r flag
RUN groupadd -g ${GID} -o app
RUN useradd -m -u ${UID} -g ${GID} -o -s /bin/bash app

RUN apt-get update -yqq && apt-get install -yqq --no-install-recommends \
  python3-dev \ 
  build-essential \ 
  pkg-config \
  vim-tiny \
  curl \
  unzip

# Set the working directory to /app
WORKDIR /app

# Download rocfl and place in /usr/local/bin
RUN curl -LO https://github.com/pwinckles/rocfl/releases/download/v1.7.0/rocfl-linux-x86_64-no-s3.zip && \
  unzip -d /usr/local/bin rocfl-linux-x86_64-no-s3.zip

# Install rust toolchain
USER app
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/home/app/.cargo/bin:$PATH"

USER root
CMD ["tail", "-f", "/dev/null"]

# Both build and development need poetry, so it is its own step.
FROM base AS poetry

RUN pip install poetry==${POETRY_VERSION}

# Use this page as a reference for python and poetry environment variables: https://docs.python.org/3/using/cmdline.html#envvar-PYTHONUNBUFFERED
# Ensure the stdout and stderr streams are sent straight to terminal, then you can see the output of your application
ENV PYTHONUNBUFFERED=1\
  # Avoid the generation of .pyc files during package install
  # Disable pip's cache, then reduce the size of the image
  PIP_NO_CACHE_DIR=off \
  # Save runtime because it is not look for updating pip version
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  # Disable poetry interaction
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=1 \
  POETRY_VIRTUALENVS_IN_PROJECT=1 \
  POETRY_CACHE_DIR=/tmp/poetry_cache

FROM poetry AS build
# Just copy the files needed to install the dependencies
COPY pyproject.toml poetry.lock README.md ./

#Use poetry to create a requirements.txt file. Dont include development dependencies
RUN poetry export --without dev -f requirements.txt --output requirements.txt

# We want poetry on in development
FROM poetry AS development
RUN apt-get update -yqq && apt-get install -yqq --no-install-recommends \
  git

# Switch to the non-root user "user"
USER app

# We don't want poetry on in production, so we copy the needed files form the build stage
FROM base AS production
# Switch to the non-root user "user"
# RUN mkdir -p /venv && chown ${UID}:${GID} /venv


COPY --chown=${UID}:${GID} . /app
COPY --chown=${UID}:${GID} --from=build "/app/requirements.txt" /app/requirements.txt

RUN pip install -r /app/requirements.txt

USER app