from dor.adapters import catalog
from fastapi import FastAPI, APIRouter

from .catalog import catalog_router

app = FastAPI()

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(catalog_router)
app.include_router(api_router)

