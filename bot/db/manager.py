import aiosqlite


class Database:
    def __init__(self):
        self.db = aiosqlite.connect(database='bot/db/statistics.db')
