from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.messages import RequestWebView

from utils import launch, scripts
from utils.emojis import rwarning, rdeny, rcheck
from utils.launch_farming import clients



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
    url = web_view.url
    await message.edit(url, disable_web_page_preview=True)


@Client.on_message(filters.me & filters.chat('me') & filters.command('farm', prefixes='/'))
@scripts.with_args('<b>This command does not work without arguments\n'
                   'Type <code>/farm on</code> to start or <code>/farm off</code> to stop</b>')
async def launch_farming(client: Client, message: Message):
    flag = scripts.get_command_args(message, 'farm')

    flags_to_start = ['on', 'start']
    flags_to_stop = ['off', 'stop']

    if flag in flags_to_start:
        await message.edit(f"{rcheck()}Farming started!")
        await launch(clients=clients)
    elif flag in flags_to_stop:
        status = await scripts.stop_task(client=client)
        await message.edit(status)


@Client.on_message(filters.me & filters.chat('me') & filters.command('balance'))
async def send_my_balance(client: Client, message: Message):
    ...


@Client.on_message(filters.me & filters.chat('me') & filters.command('help', prefixes='/'))
async def send_help_text(client: Client, message: Message):
    ...


@Client.on_message(filters.me & filters.chat('me') & filters.command('stats', prefixes='/'))
async def send_stats(client: Client, message: Message):
    ...

