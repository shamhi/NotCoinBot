import asyncio
import contextlib

from bot.utils.logging import logger
from bot.utils.launch import start_process


async def main() -> None:
    await start_process(logger=logger)


if __name__ == '__main__':
    # import logging
    # logging.basicConfig(level=logging.INFO)

    with contextlib.suppress(KeyboardInterrupt, SystemExit, UnicodeDecodeError, RuntimeError):
        asyncio.run(main())

        input('\n\nPress Enter to Exit..')
