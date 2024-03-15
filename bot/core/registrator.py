import json

import pyrogram
from loguru import logger

from bot.config import config


async def create_sessions() -> None:
    API_ID: int | str = config.API_ID
    API_HASH: str = config.API_HASH

    if not API_ID or not API_HASH:
        API_ID: int | str = input('\nВведите ваш API_ID (для выхода нажмите Enter): ')
        API_HASH: str = input('\nВведите ваш API_HASH (для выхода нажмите Enter): ')

    session_name: str = input('\nВведите название сессии (для выхода нажмите Enter): ')

    if not session_name or not API_ID or not API_HASH:
        return

    config_data = {
        'API_ID': API_ID,
        'API_HASH': API_HASH
    }

    with open('settings.json', 'w') as file:
        json.dump(config_data, file, indent=4, ensure_ascii=False)

    session: pyrogram.Client = pyrogram.Client(
        api_id=API_ID,
        api_hash=API_HASH,
        name=session_name,
        workdir="sessions/"
    )

    async with session:
        user_data = await session.get_me()

    logger.success(f'Успешно добавлена сессия @{user_data.username} | {user_data.first_name} {user_data.last_name}')
