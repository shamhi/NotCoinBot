import asyncio
import contextlib
from sys import stderr

from loguru import logger

from bot.db.manager import Database
from bot.utils import start_process


logger.remove()
logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                          ' | <level>{level: <8}</level>'
                          ' | <cyan>{line}</cyan>'
                          ' - <white>{message}</white>')

async def main() -> None:
    # Database on_startup

    await start_process(logger=logger)


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.INFO)

    with contextlib.suppress(KeyboardInterrupt, SystemExit, UnicodeDecodeError, RuntimeError):
        asyncio.run(main())

        input('\n\nPress Enter to Exit..')
