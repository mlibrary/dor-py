from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from dor.adapters import catalog
from fastapi import FastAPI, APIRouter, Request, status
import logging

from .catalog import catalog_router
from .filesets import filesets_router

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	form_data = await request.form()
	content = {'status_code': 10422, 'message': exc_str, 'data': None, 'request':f"{dict(form_data)}"}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(catalog_router)
api_router.include_router(filesets_router)
app.include_router(api_router)
