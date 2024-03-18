import asyncio

from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import HTTPException

from web.utils.models import ClickStatus
from bot.utils.logging import logger
from bot.utils import launcher, scripts


api_router = APIRouter(prefix="/api/v1")


@api_router.post(path='/clickOn')
async def clicker_on():
    try:
        session_files = launcher.get_session_files()
        clients = await launcher.get_clients(session_files=session_files)

        ...  # TODO: Soon

    except Exception as er:
        raise HTTPException(detail=er, status_code=500)

    return JSONResponse(content={"ok": True}, status_code=200)


@api_router.post(path='/clickOff')
async def clicker_on():
    try:
        await scripts.stop_task()
    except Exception as er:
        raise HTTPException(detail=er, status_code=500)

    return JSONResponse(content={"ok": True}, status_code=200)


@api_router.get(path='/getLogs')
async def get_logs():
    with open('temp-logs.txt', 'r', encoding='utf-8') as f:
        logs = f.read()

    ...  # TODO: Soon

    return PlainTextResponse(content=logs, status_code=200)
