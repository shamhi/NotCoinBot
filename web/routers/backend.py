from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

from web.utils.models import ClickStatus


api_router = APIRouter(prefix="/api/v1")


@api_router.post(path='/clickOn')
async def clicker_on(status: ClickStatus):
    return JSONResponse(content={"ok": True}, status_code=200)


@api_router.post(path='/clickOff')
async def clicker_on(status: ClickStatus):
    return JSONResponse(content={"ok": True}, status_code=200)


@api_router.get(path='/getLogs')
async def get_logs():
    with open('temp-logs.txt', 'r', encoding='utf-8') as f:
        logs = f.read()
    print(logs)
    return PlainTextResponse(content=logs, status_code=200)
