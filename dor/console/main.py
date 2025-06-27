from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

console_router = APIRouter(prefix="/console")

templates = Jinja2Templates(directory="dor/console/templates")

@console_router.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request, name="dashboard.html", context={}
    )