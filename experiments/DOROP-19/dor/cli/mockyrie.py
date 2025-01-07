import typer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from faker import Faker
import json

from dor.mockyrie.persistence.metadata_adapter import MetadataAdapter
from dor.mockyrie.models import Asset, Monograph

from dor.settings import S

import datetime

import logging
logging.basicConfig(level=logging.INFO)

from pydantic import TypeAdapter

def get_engine(echo=False):
    engine = create_engine(S.engine_url, echo=echo)
    return engine

def get_session(echo=False):
    engine = get_engine(echo=echo)
    return Session(engine)

app = typer.Typer()

@app.command()
def setup():
    adapter = MetadataAdapter(session=get_session())
    adapter.setup()

    print("setup")

@app.command()
def set_alternate_id(id: int, alternate_identifier: str):
    adapter = MetadataAdapter(session=get_session())
    resource = adapter.query_service.find_by(id)
    resource.alternate_ids.append({
        "id": alternate_identifier
    })
    resource = adapter.persister.save(resource=resource)
    print(resource)


@app.command()
def save_monograph(alternate_identifier: str = None, num_assets: int = 0, echo: bool = False):
    faker = Faker()
    with get_engine(echo=echo).connect() as conn:
        with Session(bind=conn) as session:
            adapter = MetadataAdapter(session=session)
            resource = Monograph()
            resource.created_at = datetime.datetime.now(datetime.UTC)
            resource.updated_at = resource.created_at
            resource.metadata = {"common": {"title": faker.sentence()}}
            if alternate_identifier:
                resource.alternate_ids.append({"id": alternate_identifier})

            for _ in range(0, num_assets):
                asset = Asset()
                asset.created_at = datetime.datetime.now(datetime.UTC)
                asset.updated_at = resource.created_at
                asset.metadata = {"common": {
                    "title": faker.sentence(),
                    "partOf": resource.metadata['common']['title']
                }}
                asset = adapter.persister.save(resource=asset)
                resource.member_ids.append({
                    "id": asset.id,
                    "rel": "external"
                })

            resource = adapter.persister.save(resource=resource)

    print(f"∆ save_monograph: {resource} / {len(resource.member_ids)} assets")

@app.command()
def find_all():
    adapter = MetadataAdapter(session=get_session())
    resources = adapter.query_service.find_all()

    for index, resource in enumerate(resources):
        print(f"[{index}] {resource}")

    print(f"∆ find_all: {len(resources)} total")

@app.command()
def find_by(id: int):
    adapter = MetadataAdapter(session=get_session())

    try:
        resource = adapter.query_service.find_by(id)
        print(f"∆ find_by {resource}")
    except Exception:
        print(f"⚀ find_by", id, "404 Not Found")

@app.command()
def find_by_alternate_identifier(alternate_identifier: str):
    adapter = MetadataAdapter(session=get_session())

    try:
        resource = adapter.query_service.find_by_alternate_identifier(alternate_identifier)
        print(f"∆ find_by_alternate_identifier : {alternate_identifier} -> {resource}")
    except Exception as e:
        print("⚀ find_by_alternate_identifier", alternate_identifier, "404 Not Found", e)

@app.command()
def find_members(id: int):
    adapter = MetadataAdapter(session=get_session())
    resource = adapter.query_service.find_by(id)
    members = adapter.query_service.find_members(resource)
    print(f"∆ find_members {resource}")
    for member in members:
        print("\t-", member)

@app.command()
def dump_resource(id: int):
    adapter = MetadataAdapter(session=get_session())
    resource = adapter.query_service.find_by(id)
    print(f"∆ dump_resource {resource}")
    print(TypeAdapter(resource.__class__).dump_json(resource, indent=2).decode('utf-8'))

@app.command()
def update_monograph(id: int, key: str = 'title', value: str = 'xyzzy'):
    adapter = MetadataAdapter(session=get_session())
    resource = adapter.query_service.find_by(id)
    resource.metadata['common'][key] = value
    resource = adapter.persister.save(resource=resource)

    print(f"∆ update_monograph {resource}")
    print(TypeAdapter(resource.__class__).dump_json(resource, indent=2).decode("utf-8"))
