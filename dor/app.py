import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from dor.entrypoints.api.main import api_router
from dor.console.main import console_router

app = FastAPI()

app.mount("/static", StaticFiles(directory="dor/static"), name="static")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	form_data = await request.form()
	content = {'status_code': 10422, 'message': exc_str, 'data': None, 'request':f"{dict(form_data)}"}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

app.include_router(api_router)
app.include_router(console_router)
