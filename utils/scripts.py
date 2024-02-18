import asyncio
from json import loads
from typing import Union

from pyrogram import Client
from pyrogram.types import Message
from better_proxy import Proxy
from loguru import logger
from aiofiles.ospath import exists
import aiofiles

from utils.emojis import rcheck, rwarning


def get_command_args(message: Union[Message, str], command: Union[str, list[str]] = None, prefixes: str = '/') -> str:
    if isinstance(message, str):
        return message.split(f'{prefixes}{command}', maxsplit=1)[-1].strip()

    if isinstance(command, str):
        args = message.text.split(f'{prefixes}{command}', maxsplit=1)[-1].strip()
        return args

    elif isinstance(command, list):
        for cmd in command:
            args = message.text.split(f'{prefixes}{cmd}', maxsplit=1)[-1]

            if args != message.text:
                return args.strip()

    return ''


def with_args(text: str):
    def decorator(func):
        async def wrapped(client: Client, message: Message):
            if message.text and len(message.text.split()) == 1:
                await message.edit(f'<emoji id=5210952531676504517>❌</emoji>{text}')
            else:
                return await func(client, message)

        return wrapped

    return decorator


def get_proxy_dict(session_proxy: str | None) -> Proxy | None:
    try:
        proxy: Proxy = Proxy.from_str(
            proxy=session_proxy
        )

        proxy_dict: dict = {
            'proxy_type': proxy.protocol,
            'addr': proxy.host,
            'port': proxy.port,
            'username': proxy.login,
            'password': proxy.password
        }

    except ValueError:
        logger.error(f'Неверно указан Proxy, повторите попытку ввода')
        proxy_dict: None = None

    return proxy_dict


def get_value(file_json: dict,
              *keys) -> str | None:
    for key in keys:
        if key in file_json:
            return file_json[key]
    return None


async def read_session_json_file(session_name: str) -> dict:
    file_path: str = f'sessions/{session_name}.json'
    result_dict: dict = {}

    try:
        if not await exists(file_path):
            return result_dict

        async with aiofiles.open(file=file_path,
                                 mode='r',
                                 encoding='utf-8') as file:
            file_json: dict = loads(await file.read())

        result_dict: dict = {
            'api_id': get_value(file_json, 'api_id', 'app_id', 'apiId', 'appId'),
            'api_hash': get_value(file_json, 'api_hash', 'app_hash', 'apiHash', 'appHash'),
            'device_model': get_value(file_json, 'deviceModel', 'device'),
            'system_version': get_value(file_json, 'systemVersion', 'system_version', 'appVersion', 'app_version'),
            'app_version': get_value(file_json, 'appVersion', 'app_version'),
            'lang_code': get_value(file_json, 'lang_pack', 'langCode', 'lang'),
            'system_lang_code': get_value(file_json, 'system_lang_pack', 'systemLangCode', 'systemLangPack')
        }

    except Exception as error:
        logger.error(f'{session_name} | Ошибка при чтении .json файла: {error}')

    return result_dict


async def stop_task(client: Client = None) -> str:
    if client:
        all_tasks = asyncio.all_tasks(loop=client.loop)
    else:
        loop = asyncio.get_event_loop()
        all_tasks = asyncio.all_tasks(loop=loop)

    farming_tasks = [task for task in all_tasks
                     if isinstance(task, asyncio.Task) and task._coro.__name__ in ['start_farming', 'run', 'launch', 'Farming']]

    for task in farming_tasks:
        try:
            task.cancel()
        except:
            ...

    return f'<b>{rcheck()}The clicker process has stopped</b>'
