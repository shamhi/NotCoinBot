import contextlib

from tortoise import run_async

from db import on_startup_db
from bot.utils.logging import logger
from bot.utils.launcher import start_process


async def main() -> None:
    await on_startup_db()
    await start_process(logger=logger)


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.INFO)

    with contextlib.suppress(KeyboardInterrupt, SystemExit, UnicodeDecodeError, RuntimeError):
        run_async(main())

        input('\n\nPress Enter to Exit..')
