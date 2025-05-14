#!/usr/bin/env bash

if [ -f ".env" ]; then
  echo "🌎 .env exists. Leaving alone"
else
  echo "🌎 .env does not exist. Copying .env-example to .env"
  cp env.example .env
  YOUR_UID=`id -u`
  YOUR_GID=`id -g`
  echo "🙂 Setting your UID ($YOUR_UID) and GID ($YOUR_UID) in .env"
  docker run --rm -v ./.env:/.env alpine echo "$(sed s/YOUR_UID/$YOUR_UID/ .env)" > .env
  docker run --rm -v ./.env:/.env alpine echo "$(sed s/YOUR_GID/$YOUR_GID/ .env)" > .env
fi

echo "🚢 Build docker images"
docker compose build

echo "📦 Build python packages"
docker compose run --rm app poetry install

FILESET_DIR="data/filesets"
if [ ! -d "$FILESET_DIR" ]; then
  echo "Creating directory: $FILESET_DIR"
  mkdir -p "$FILESET_DIR"
  chmod 755 "$FILESET_DIR"
fi
