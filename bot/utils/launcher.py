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
from bot.core import run_clicker, create_sessions
from bot.exceptions import InvalidSession




clients = []


def get_session_files() -> list[str]:
    session_files = glob.glob('sessions/*.session')
    session_files = [os.path.splitext(os.path.basename(file))[0] for file in session_files]

    return session_files


def get_proxies() -> list[Proxy]:
    if settings.USE_PROXY_FROM_FILE:
        with open(file='bot/config/proxies.txt',
                  mode='r',
                  encoding='utf-8-sig') as file:
            proxies: list[Proxy] = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies


async def get_session_string(session_name: str):
    session = None
    for action in [SessionManager.from_pyrogram_file, SessionManager.from_telethon_file]:
        try:
            session = await action(f'sessions/{session_name}.session')
        except Exception as ex:
            print(ex)
            ...
        else:
            break

    if not session:
        raise InvalidSession(session_name)

    return session.to_pyrogram_string()


async def get_clients(session_files: list[str]):
    if not session_files:
        raise FileNotFoundError("Not found session files")

    if not settings.API_ID or not settings.API_HASH:
        raise ValueError("API_ID and API_HASH not found in the .env file.")

    global clients

    clients = [Client(
        name=session_name,
        api_id=settings.API_ID,
        api_hash=settings.API_HASH,
        session_string=(await get_session_string(session_name=session_name)),
        workdir='sessions/',
        plugins=dict(root='bot/plugins')
    ) for session_name in session_files]

    return clients


async def start_process(logger: Logger):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    args = parser.parse_args()

    session_files: list[str] = get_session_files()
    proxies: list[Proxy] = get_proxies()

    logger.info(f"Обнаружено {len(session_files)} сессий / {len(proxies)} прокси")

    await asyncio.sleep(delay=.25)

    user_action: Literal[1, 2, 3] = args.action if args.action else int(input(
        "\n1. Создать сессию"
        "\n2. Запустить бота С возможностью управления через телеграмм"
        "\n3. Запустить бота БЕЗ возможности управления через телеграмм"
        "\nВыберите ваше действие: "
    ))
    print()

    match user_action:
        case 1:
            await create_sessions()

        case 2:
            clients = await get_clients(session_files=session_files)

            logger.info(f"Бот запущен на {len(session_files)} сессиях.\n"
                        f"Отправьте /help в чате Избранное/Saved Messages \n")

            await compose(clients)

        case 3:
            clients = await get_clients(session_files=session_files)

            logger.info("Бот запущен без возможности управления через телеграмм")

            await run_tasks(clients=clients)

        case _:
            logger.error("Действие выбрано некорректно")


async def run_tasks(clients: list[Client]):
    session_files = get_session_files()
    proxies = get_proxies()
    proxies_cycled = cycle(proxies) if proxies else None

    tasks: list = [
        asyncio.create_task(coro=run_clicker(
            session_name=current_session_name, client=client, proxy=next(proxies_cycled) if proxies_cycled else None)
        )
        for client, current_session_name in zip(clients, session_files)
    ]

    await asyncio.gather(*tasks)

    print('after bot')
