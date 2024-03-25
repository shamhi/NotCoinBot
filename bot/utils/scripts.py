import asyncio
from typing import Union
from datetime import datetime

from pyrogram import Client
from pyrogram.types import Message
from better_proxy import Proxy
from loguru import logger

from bot.utils.emojis import num, StaticEmoji


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
        proxy: Proxy = Proxy.from_str(proxy=session_proxy)

        proxy_dict: dict = dict(
            scheme=proxy.protocol,
            hostname=proxy.host,
            port=proxy.port,
            username=proxy.login,
            password=proxy.password
        )

    except ValueError:
        logger.error(f'Неверно указан Proxy, повторите попытку ввода')
        proxy_dict: None = None

    return proxy_dict


def get_bad_statuses_count(request_statuses: list[str]) -> int:
    count = 0
    for status in request_statuses:
        if status.startswith('2'):
            count = 0
            continue

        count += 1

    return count


def get_help_text():
    return f"""<b>
{StaticEmoji.FLAG} [Демо версия]

{num(1)} /help - Выводит все доступные команды
{num(2)} /click [on|start, off|stop] - Запускает или останавливает кликер
{num(3)} /balance - выводит текущий баланс
{num(4)} /stat - Выводит статистику запущенного кликера
</b>"""


def get_stat_text(session_name: str,
                  start_balance: int,
                  end_balance: int,
                  start_datetime: datetime,
                  end_datetime: datetime) -> str:
    income = ''.join([num(n) for n in str(end_balance-start_balance)])
    start_balance = ''.join([num(n) for n in str(start_balance)])
    end_balance = ''.join([num(n) for n in str(end_balance)])
    start_datetime = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    end_datetime = end_datetime.strftime("%Y-%m-%d %H:%M:%S")

    return f"""<b>
{StaticEmoji.FLAG} [Демо версия]
    
{StaticEmoji.LOUDSPEAKER}Статистика {session_name} с {start_datetime} по {end_datetime}

{StaticEmoji.SCRAP} Начальный баланс: {start_balance} {StaticEmoji.DOLLAR}
{StaticEmoji.ARROW} Текущий баланс: {end_balance} {StaticEmoji.DOLLAR}
{StaticEmoji.PLUS} Заработано: {income} {StaticEmoji.DOLLAR}
</b>"""


def get_balance_text(balance: int):
    balance = ''.join([num(n) for n in str(balance)])

    return f"<b>Ваш текущий баланс: {balance} {StaticEmoji.DOLLAR}</b>"


async def stop_tasks(client: Client = None) -> None:
    if client:
        all_tasks = asyncio.all_tasks(loop=client.loop)
    else:
        loop = asyncio.get_event_loop()
        all_tasks = asyncio.all_tasks(loop=loop)

    clicker_tasks = [task for task in all_tasks
                     if isinstance(task, asyncio.Task) and task._coro.__name__ in ['run_clicker']]

    for task in clicker_tasks:
        try:
            task.cancel()
        except:
            ...
