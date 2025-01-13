import uuid

from dor.config import config
from dor.service_layer import catalog_service
import sqlalchemy
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from dor.adapters.catalog import SqlalchemyCatalog


catalog_router = APIRouter(prefix="/catalog")

ENGINE = sqlalchemy.create_engine(config.get_database_engine_url())


def get_db_session():
    with sqlalchemy.orm.Session(ENGINE) as session:
        yield session


@catalog_router.get("/bins/{identifier}/")
def get_bin_summary(identifier: str, session = Depends(get_db_session)) -> JSONResponse:
    try:
        uuid_identifier = uuid.UUID(identifier)
    except ValueError:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Identifier is not a valid UUID.")

    catalog = SqlalchemyCatalog(session)
    bin = catalog.get(uuid_identifier)
    if bin:
        summary = catalog_service.summarize(bin)
        return JSONResponse(status_code=status.HTTP_200_OK, content=summary)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Item not found")


@catalog_router.get("/bins/{identifier}/filesets")
def get_bin_filesets(identifier: str, session = Depends(get_db_session)) -> JSONResponse:
    try:
        uuid_identifier = uuid.UUID(identifier)
    except ValueError:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Identifier is not a valid UUID.")

    catalog = SqlalchemyCatalog(session)
    bin = catalog.get(uuid_identifier)
    if bin:
        filesets = catalog_service.get_file_sets(bin)
        return JSONResponse(status_code=status.HTTP_200_OK, content=filesets)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Item not found")
