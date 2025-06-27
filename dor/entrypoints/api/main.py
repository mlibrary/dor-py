from fastapi import APIRouter

from .catalog import catalog_router
from .filesets import filesets_router
from .packages import packages_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(catalog_router)
api_router.include_router(filesets_router)
api_router.include_router(packages_router)
