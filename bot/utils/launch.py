import os
import glob
import asyncio
import argparse
from itertools import cycle

from pyrogram import Client, compose
from better_proxy import Proxy
from loguru._logger import Logger

from config import settings
from bot.core import run_clicker, create_sessions


clients = []


def get_session_files():
    session_files = glob.glob('sessions/*.session')
    session_files = [os.path.splitext(os.path.basename(file))[0] for file in session_files]

    return session_files


def get_proxies():
    if settings.USE_PROXY_FROM_FILE:
        with open(file='bot/config/proxies.txt',
                  mode='r',
                  encoding='utf-8-sig') as file:
            proxies: list[str] = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies


async def start_process(logger: Logger):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    args = parser.parse_args()

    session_files = get_session_files()
    proxies = get_proxies()

    logger.info(f'Обнаружено {len(session_files)} сессий / {len(proxies)} прокси')

    await asyncio.sleep(delay=.25)

    user_action: int = args.action if args.action else int(input(
        '\n1. Создать сессию'
        '\n2. Запустить бота С возможностью управления через телеграмм'
        '\n3. Запустить бота БЕЗ возможности управления через телеграмм'
        '\nВыберите ваше действие: '
    ))
    print()

    match user_action:
        case 1:
            await create_sessions()

        case 2:
            if not session_files:
                raise FileNotFoundError("Not found session files")

            if not settings.API_ID or not settings.API_HASH:
                raise ValueError("API_ID and API_HASH not found in the .env file.")

            logger.info(f'Бот запущен на {len(session_files)} сессиях.\n'
                        f'Отправьте /help в чате Избранное/Saved Messages \n')

            global clients

            clients = [Client(
                name=name,
                api_id=settings.API_ID,
                api_hash=settings.API_HASH,
                workdir='sessions/',
                plugins=dict(root='bot/plugins')
            ) for name in session_files]

            await compose(clients)

        case 3:
            if not session_files:
                raise FileNotFoundError("Not found session files")

            if not settings.API_ID or not settings.API_HASH:
                raise ValueError("API_ID and API_HASH not found in the .env file.")

            logger.info(f'Бот запущен без возможности управления через телеграмм \n')

            clients = [Client(
                name=name,
                api_id=settings.API_ID,
                api_hash=settings.API_HASH,
                workdir='sessions/',
                plugins=dict(root='bot/plugins')
            ) for name in session_files]

            await run_tasks(clients=clients)

        case _:
            logger.error('Действие выбрано некорректно')


async def run_tasks(clients: list[Client]):
    session_files = get_session_files()
    proxies = get_proxies()
    proxies_cycled = cycle(proxies) if proxies else None

    tasks: list = [
        asyncio.create_task(
            coro=run_clicker(session_name=current_session_name,
                             client=client,
                             proxy=next(proxies_cycled) if proxies_cycled else None))
        for client, current_session_name in zip(clients, session_files)
    ]

    await asyncio.gather(*tasks)
