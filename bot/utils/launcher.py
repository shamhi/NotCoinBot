import os
import glob
import asyncio
import argparse
from itertools import cycle
from typing import Literal

from TGConvertor import SessionManager
from pyrogram import Client, compose
from better_proxy import Proxy
from loguru._logger import Logger

from config import settings
from bot.core import run_clicker, register_sessions
from db.functions import check_sessions


tg_clients = []


def get_session_names() -> list[str]:
    session_names = glob.glob('sessions/*.session')
    session_names = [os.path.splitext(os.path.basename(file))[0] for file in session_names]

    return session_names


def get_proxies() -> list[Proxy]:
    if settings.USE_PROXY_FROM_FILE:
        with open(file='config/proxies.txt',
                  mode='r',
                  encoding='utf-8-sig') as file:
            proxies: list[Proxy] = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies


async def get_session_string(session_name: str) -> str | None:
    session = None
    for action in [SessionManager.from_pyrogram_file, SessionManager.from_telethon_file]:
        try: session = await action(f'sessions/{session_name}.session')
        except: ...
        else: break

    if not session:
        return None

    return session.to_pyrogram_string()


async def get_clients(session_names: list[str]) -> list[Client]:
    if not session_names:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    global tg_clients

    tg_clients = [Client(
        name=session_name,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        session_string=(await get_session_string(session_name=session_name)),
        workdir='sessions/',
        plugins=dict(root='bot/plugins')
    ) for session_name in session_names]

    await check_sessions(session_names=session_names, tg_clients=tg_clients)

    return tg_clients


async def start_process(logger: Logger) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    args = parser.parse_args()

    session_names: list[str] = get_session_names()
    proxies: list[Proxy] = get_proxies()

    logger.info(f"Обнаружено {len(session_names)} сессий / {len(proxies)} прокси")

    await asyncio.sleep(delay=.25)

    user_action: Literal[1, 2, 3] = args.action if args.action else int(input(
        "\n1. Создать сессию"
        "\n2. Запустить бота С возможностью управления через телеграмм"
        "\n3. Запустить бота БЕЗ возможности управления через телеграмм"
        "\nВыберите ваше действие: "
    ))
    print()

    if user_action == 1:
        await register_sessions()

    elif user_action == 2:
        tg_clients = await get_clients(session_names=session_names)

        logger.info(f"Бот запущен на {len(session_names)} сессиях.\n"
                    f"Отправьте /help в чате Избранное/Saved Messages \n")

        await compose(tg_clients)

    elif user_action == 3:
        tg_clients = await get_clients(session_names=session_names)

        logger.info("Бот запущен без возможности управления через телеграмм")

        await run_tasks(tg_clients=tg_clients)

    else:
        logger.error("Действие выбрано некорректно")


async def run_tasks(tg_clients: list[Client]):
    session_names = get_session_names()
    proxies = get_proxies()
    proxies_cycled = cycle(proxies) if proxies else None

    tasks: list = [
        asyncio.create_task(coro=run_clicker(
            session_name=current_session_name, tg_client=client, proxy=next(proxies_cycled) if proxies_cycled else None)
        )
        for client, current_session_name in zip(tg_clients, session_names)
    ]

    await asyncio.gather(*tasks)
