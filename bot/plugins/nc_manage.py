from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.messages import RequestWebView

from bot.utils import scripts
from bot.utils.logging import logger
from bot.utils.emojis import StaticEmoji
from bot.utils.launcher import tg_clients, run_tasks
from db.functions import (get_session_id, get_start_balance, get_end_balance, get_start_datetime, get_end_datetime,
                          get_session_name)


@Client.on_message(filters.me & filters.private & filters.chat('me') & filters.command('ncu', prefixes='/'))
async def get_notcoin_url(client: Client, message: Message):
    web_view = await client.invoke(
        RequestWebView(
            peer=await client.resolve_peer('notcoin_bot'),
            bot=await client.resolve_peer('notcoin_bot'),
            platform='android',
            from_bot_menu=False,
            url='https://clicker.joincommunity.xyz/clicker'
        )
    )
    url = web_view.url.replace('tgWebAppVersion=6.7', 'tgWebAppVersion=7.0')
    await message.edit(url, disable_web_page_preview=True)


@Client.on_message(filters.me & filters.chat('me') & filters.command('click', prefixes='/'))
@scripts.with_args('<b>Эта команда не работает без аргументов\n'
                   'Введите <code>/click on</code> для запуска или <code>/click off</code> для остановки</b>')
async def launch_clicker(client: Client, message: Message):
    flag = scripts.get_command_args(message, 'click')

    flags_to_start = ['on', 'start']
    flags_to_stop = ['off', 'stop']

    if flag in flags_to_start:
        logger.info(f"Кликер запущен командой /click {flag}\n")

        await message.edit(f"<b>{StaticEmoji.ACCEPT} Кликер запущен! {StaticEmoji.START}</b>")
        await run_tasks(tg_clients=tg_clients)
    elif flag in flags_to_stop:
        logger.info(f"Кликер остановлен командой /click {flag}\n")

        await scripts.stop_tasks(client=client)
        await message.edit(f'<b>{StaticEmoji.ACCEPT} Кликер остановлен! {StaticEmoji.STOP}</b>')
    else:
        await message.edit(f"<b>{StaticEmoji.DENY} Эта команда принимает только аргументы: on/off | start/stop</b>")


@Client.on_message(filters.me & filters.chat('me') & filters.command('help', prefixes='/'))
async def send_help_text(_: Client, message: Message):
    help_text = scripts.get_help_text()

    await message.edit(text=help_text)


@Client.on_message(filters.me & filters.chat('me') & filters.command('balance'))
async def send_my_balance(client: Client, message: Message):
    session_id = await get_session_id(tg_id=client.me.id)
    balance = await get_end_balance(session_id=session_id)

    balance_text = scripts.get_balance_text(balance=balance)

    await message.edit(text=balance_text)


@Client.on_message(filters.me & filters.chat('me') & filters.command('stat', prefixes='/'))
async def send_stats(client: Client, message: Message):
    session_id = await get_session_id(tg_id=client.me.id)
    session_name = await get_session_name(session_id=session_id)

    start_balance = await get_start_balance(session_id=session_id)
    end_balance = await get_end_balance(session_id=session_id)
    start_datetime = await get_start_datetime(session_id=session_id)
    end_datetime = await get_end_datetime(session_id=session_id)

    stat_text = scripts.get_stat_text(session_name=session_name,
                                      start_balance=start_balance,
                                      end_balance=end_balance,
                                      start_datetime=start_datetime,
                                      end_datetime=end_datetime)

    await message.edit(text=stat_text)
