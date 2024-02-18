import os
import asyncio
import argparse
from itertools import cycle

from pyrogram import Client, compose
from better_proxy import Proxy
from loguru._logger import Logger

from core import start_farming, create_sessions
from database import get_session_names
from data import config


clients = []


def get_session_files():
    session_files: list[str] = [
        current_file[:-8] if current_file.endswith('.session')
        else current_file for current_file in os.listdir(path='sessions/')
        if current_file.endswith('.session') or os.path.isdir(s=f'sessions/{current_file}')
    ]

    return session_files


def get_proxies():
    if config.USE_PROXY_FROM_FILE:
        with open(file='data/proxies.txt',
                  mode='r',
                  encoding='utf-8-sig') as file:
            proxies: list[str] = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    return proxies


async def launch_process(logger: Logger):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    args = parser.parse_args()

    session_files = get_session_files()
    proxies = get_proxies()

    logger.info(f'Обнаружено {len(session_files)} сессий / {len(proxies)} прокси')

    await asyncio.sleep(delay=1)

    user_action: int = args.action if args.action else int(input(
        '\n1. Создать сессию'
        '\n2. Запустить бота С возможностью управления через телеграмм'
        '\n3. Запустить бота БЕЗ возможности управления через телеграмм'
        '\nВыберите ваше действие: '
    ))
    print()

    match user_action:
        case 1:
            sessions = await create_sessions()

            if sessions:
                logger.success('Сессии успешно добавлены')
            else:
                logger.warning('Отмена')

        case 2:
            if not session_files:
                raise FileNotFoundError("Not found session files")

            logger.info(f'Бот запущен на {len(session_files)} сессиях. '
                        f'Отправьте /help в чате Избранное/Saved Messages \n')

            global clients

            clients = [Client(
                name=name,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                workdir='sessions/',
                plugins=dict(root='plugins')
            ) async for name in get_session_names()]

            await compose(clients)

        case 3:
            logger.info(f'Бот запущен без возможности управления через телеграмм \n')

            clients = [Client(
                name=name,
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                workdir='sessions/',
                plugins=dict(root='plugins')
            ) async for name in get_session_names()]

            await launch(clients=clients)
        case _:
            logger.error('Действие выбрано некорректно')


async def launch(clients: list[Client]):
    session_files = get_session_files()
    proxies = get_proxies()
    proxies_cycled = cycle(proxies) if proxies else None


    tasks: list = [
        asyncio.create_task(coro=start_farming(session_name=current_session_name,
                                               client=client,
                                               proxy=next(proxies_cycled) if proxies_cycled else None))
        for client, current_session_name in zip(clients, session_files)
    ]

    await asyncio.gather(*tasks)
