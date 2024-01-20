from itertools import cycle
from os.path import isdir
from os import listdir
from os import mkdir
from os.path import exists, isfile
from sys import stderr
import argparse
import asyncio

from loguru import logger
from better_proxy import Proxy

from core import create_sessions, start_farming
from database import on_startup_database
from data import config
from utils import monkeypatching


logger.remove()
logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                          ' | <level>{level: <8}</level>'
                          ' | <cyan>{line}</cyan>'
                          ' - <white>{message}</white>')


async def main() -> None:
    await on_startup_database()

    match user_action:
        case 1:
            sessions = await create_sessions()

            if sessions:
                logger.success('Сессии успешно добавлены')
            else:
                logger.warning('Отмена')

        case 2:
            tasks: list = [
                asyncio.create_task(coro=start_farming(session_name=current_session_name,
                                                       proxy=next(proxies_cycled) if proxies_cycled else None))
                for current_session_name in session_files
            ]

            await asyncio.gather(*tasks)

        case _:
            logger.error('Действие выбрано некорректно')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', type=int, help='Action to perform')

    args = parser.parse_args()

    if not exists(path='sessions'):
        mkdir(path='sessions')

    if not isfile(path='settings.json'):
        with open('settings.json', 'w') as file:
            file.write('')

    if not isfile(path='data/proxies.txt'):
        with open('data/proxies.txt', 'w') as file:
            file.write('')

    if config.USE_PROXY_FROM_FILE:
        with open(file='data/proxies.txt',
                  mode='r',
                  encoding='utf-8-sig') as file:
            proxies: list[str] = [Proxy.from_str(proxy=row.strip()).as_url for row in file]
    else:
        proxies = []

    if proxies:
        proxies_cycled: cycle = cycle(proxies)

    else:
        proxies_cycled: None = None

    session_files: list[str] = [current_file[:-8] if current_file.endswith('.session')
                                else current_file for current_file in listdir(path='sessions')
                                if current_file.endswith('.session') or isdir(s=f'sessions/{current_file}')]

    logger.info(f'Обнаружено {len(session_files)} сессий / {len(proxies)} прокси')

    if args.action:
        user_action = args.action
    else:
        user_action: int = int(input('\n1. Создать сессию'
                                     '\n2. Запустить бота с существующих сессий'
                                     '\nВыберите ваше действие: '))
        print()

    asyncio.run(main())

    input('\n\nPress Enter to Exit..')
