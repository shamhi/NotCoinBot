from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


front_router = APIRouter()


templates = Jinja2Templates(directory="web/templates")


@front_router.get(path='/', response_class=HTMLResponse)
async def root_template(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )
