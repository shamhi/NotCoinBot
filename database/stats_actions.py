import datetime

import aiosqlite

from database.on_startup import on_startup_database


# TODO: Soon

async def get_balance(balance):
    async with aiosqlite.connect(database='database/stats.db') as db:
        await db.execute(sql="SELECT stopped_balance ")

