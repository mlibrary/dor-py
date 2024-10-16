# PYTHON image
# Use the official Docker Python image because it has the absolute latest bugfix version of Python
# it has the absolute latest system packages
# it’s based on Debian Bookworm (Debian 12), released June 2023
# Initial Image size is 51MB
# At the end Image size is 156MB

# I did not recommed using an alpine image because it lacks the package installer pip and the support for installing
# wheel packages, which are both needed for installing applications like Pandas and Numpy.

# The base layer will contain the dependencies shared by the other layers
FROM python:3.11-slim-bookworm as base

# Allowing the argumenets to be read into the dockerfile. Ex:  .env > compose.yml > Dockerfile
ARG POETRY_VERSION=1.8.4
ARG UID=1000
ARG GID=1000

# true = development / false = production
ARG DEV

ENV PYTHONPATH="/app"

# Set the working directory to /app
WORKDIR /app

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

RUN pip install poetry==${POETRY_VERSION}

# Install the app. Just copy the files needed to install the dependencies
COPY pyproject.toml poetry.lock README.md ./

# Poetry cache is used to avoid installing the dependencies every time the code changes, we will keep this folder in development environment and remove it in production
# --no-root, poetry will install only the dependencies avoiding to install the project itself, we will install the project in the final layer
# --without dev to avoid installing dev dependencies, we do not need test and linters in production environment
# --with dev to install dev dependencies, we need test and linters in development environment
# --mount, mount a folder for plugins with poetry cache, this will speed up the process of building the image
RUN if [ {${DEV}} ]; then \
      echo "Installing dev dependencies"; \
      poetry install --no-root --with dev \
    else \
      echo "Skipping dev dependencies"; \
      poetry install --no-root --without dev && rm -rf ${POETRY_CACHE_DIR}; \
   fi

# Set up our final runtime layer
FROM python:3.11-slim-bookworm as runtime

ARG UID=1000
ARG GID=1000

# Create our users here in the last layer or else it will be lost in the previous discarded layers
# Create a system group named "app_user" with the -r flag
RUN groupadd -g ${GID} -o app
RUN useradd -m -d /app -u ${UID} -g ${GID} -o -s /bin/bash app
RUN mkdir -p /venv && chown ${UID}:${GID} /venv
RUN which pip && sleep 10

# By adding /venv/bin to the PATH the dependencies in the virtual environment
# are used
ENV VIRTUAL_ENV=/venv \
    PATH="/venv/bin:$PATH"

COPY --chown=${UID}:${GID} --from=base "/app/.venv" ${VIRTUAL_ENV}

# Switch to the non-root user "user"
USER app

WORKDIR /app

COPY --chown=${UID}:${GID} . /app

CMD ["tail", "-f", "/dev/null"]
