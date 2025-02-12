import uuid

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from dor.adapters.catalog import SqlalchemyCatalog
from dor.entrypoints.api.dependencies import get_db_session
from dor.service_layer import catalog_service


catalog_router = APIRouter(prefix="/catalog")


@catalog_router.get("/revisions/{identifier}/")
def get_revision_summary(identifier: str, session = Depends(get_db_session)) -> JSONResponse:
    try:
        uuid_identifier = uuid.UUID(identifier)
    except ValueError:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Identifier is not a valid UUID.")

    catalog = SqlalchemyCatalog(session)
    revision = catalog.get(str(uuid_identifier))
    if revision:
        summary = catalog_service.summarize(revision)
        return JSONResponse(status_code=status.HTTP_200_OK, content=summary)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Item not found")


@catalog_router.get("/revisions/{identifier}/filesets")
def get_revision_filesets(identifier: str, session = Depends(get_db_session)) -> JSONResponse:
    try:
        uuid_identifier = uuid.UUID(identifier)
    except ValueError:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Identifier is not a valid UUID.")

    catalog = SqlalchemyCatalog(session)
    revision = catalog.get(str(uuid_identifier))
    if revision:
        filesets = catalog_service.get_file_sets(revision)
        return JSONResponse(status_code=status.HTTP_200_OK, content=filesets)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content="Item not found")
