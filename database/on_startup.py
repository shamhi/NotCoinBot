import aiosqlite


async def on_startup_database() -> None:
    async with aiosqlite.connect(database='database/sessions.db') as db:
        await db.execute(sql="""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY,
            session_name TEXT,
            session_proxy TEXT
        );
        """)
        await db.commit()

    async with aiosqlite.connect(database='database/stats.db') as db:
        await db.execute(sql="""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY,
                    full_name VARCHAR(128)
                );
                """)
        await db.commit()

        await db.execute(sql="""
                CREATE TABLE IF NOT EXISTS stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id BIGINT,
                    started_balance BIGINT,
                    stopped_balance BIGINT,
                    started_at DATETIME,
                    stopped_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );
                """)
        await db.commit()
