import datetime

import aiosqlite


# TODO: Soon

async def get_balance(balance):
    async with aiosqlite.connect(database='database/stats.db') as db:
        await db.execute(sql="SELECT stopped_balance ")

