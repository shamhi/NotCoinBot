import asyncio
import logging
import contextlib
from sys import stderr

from loguru import logger

from database import on_startup_database
from utils import launch_process


logger.remove()
logger.add(stderr, format='<white>{time:HH:mm:ss}</white>'
                          ' | <level>{level: <8}</level>'
                          ' | <cyan>{line}</cyan>'
                          ' - <white>{message}</white>')

async def main() -> None:
    await on_startup_database()

    await launch_process(logger=logger)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    with contextlib.suppress(KeyboardInterrupt, SystemExit, UnicodeDecodeError, RuntimeError):
        asyncio.run(main())

        input('\n\nPress Enter to Exit..')
