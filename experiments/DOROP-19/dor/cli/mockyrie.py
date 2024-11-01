import typer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from faker import Faker
import json

from dor.mockyrie.persistence.metadata_adapter import MetadataAdapter
from dor.mockyrie.models import Asset, Monograph

import datetime

def get_engine():
    engine = create_engine("postgresql+psycopg://roger@localhost/dor_test", echo=True)
    return engine

def get_session():
    engine = create_engine("postgresql+psycopg://roger@localhost/dor_test", echo=True)
    return Session(engine)

app = typer.Typer()

@app.command()
def setup():
    adapter = MetadataAdapter(engine=get_engine())
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
def save_monograph(alternate_id: str = None, num_assets: int = 0):
    faker = Faker()
    with get_engine().connect() as conn:
        with Session(bind=conn) as session:
            adapter = MetadataAdapter(session=session)
            resource = Monograph()
            resource.created_at = datetime.datetime.now(datetime.UTC)
            resource.updated_at = resource.created_at
            resource.metadata = {"common": {"title": faker.sentence()}}
            if alternate_id:
                resource.alternate_ids.append({
                    "id": alternate_id
                })

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

    print("save_monograph", resource)

@app.command()
def find_all():
    adapter = MetadataAdapter(session=get_session())
    resources = adapter.query_service.find_all()

    for resource in resources:
        print(resource)

    print("find_all", len(resources))


@app.command()
def find_by(id: int):
    adapter = MetadataAdapter(session=get_session())

    try:
        resource = adapter.query_service.find_by(id)
        print("find_by", id, resource)
    except Exception:
        print("find_by", id, "404")


@app.command()
def find_by_alternate_identifier(alternate_identifier: str):
    adapter = MetadataAdapter(session=get_session())

    try:
        resource = adapter.query_service.find_by_alternate_identifier(alternate_identifier)
        print("find_by_alternate_identifier", alternate_identifier, resource)
    except Exception as e:
        print("find_by_alternate_identifier", alternate_identifier, "404", e)

@app.command()
def find_members(id: int):
    adapter = MetadataAdapter(session=get_session())
    resource = adapter.query_service.find_by(id)
    members = adapter.query_service.find_members(resource)
    print(resource)
    for member in members:
        print("-", member)
