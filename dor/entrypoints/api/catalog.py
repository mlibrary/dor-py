import os
import uuid

from dor.service_layer import catalog_service
import sqlalchemy
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from dor.adapters.catalog import SqlalchemyCatalog


catalog_router = APIRouter(prefix="/catalog")

url = sqlalchemy.engine.URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["POSTGRES_USER"],
    password=os.environ["POSTGRES_PASSWORD"],
    host=os.environ["POSTGRES_HOST"],
    database="dor_test"
)
ENGINE = sqlalchemy.create_engine(url)


def get_db_session():
    with sqlalchemy.orm.Session(ENGINE) as session:
        yield session


@catalog_router.get("/{identifier}/")
def get_bin_summary(identifier: str, session = Depends(get_db_session)) -> JSONResponse:
    try:
        uuid_identifier = uuid.UUID(identifier)
    except ValueError:
        return JSONResponse(status_code=401, content="Identifier is not a valid UUID.")

    catalog = SqlalchemyCatalog(session)
    bin = catalog.get(uuid_identifier)
    if bin:
        summary = catalog_service.summarize(bin)
        return JSONResponse(status_code=201, content=summary)
    else:
        return JSONResponse(status_code=404, content="Item not found")
