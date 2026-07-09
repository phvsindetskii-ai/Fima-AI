import aiosqlite

DB_NAME = "database.db"


class Database:

    def __init__(self):
        self.db = DB_NAME

    async def connect(self):
        return await aiosqlite.connect(self.db)

    async def initialize(self):
        async with await self.connect() as db:

            await db.execute("""
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            await db.execute("""
            CREATE TABLE IF NOT EXISTS messages(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)

            await db.execute("""
            CREATE TABLE IF NOT EXISTS memories(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                key TEXT,
                value TEXT
            )
            """)

            await db.commit()

    async def add_user(
        self,
        user_id: int,
        username: str,
        first_name: str
    ):
        async with await self.connect() as db:

            await db.execute(
                """
                INSERT OR IGNORE INTO users
                (user_id, username, first_name)
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    username,
                    first_name,
                ),
            )

            await db.commit()

    async def save_message(
        self,
        user_id: int,
        role: str,
        content: str
    ):
        async with await self.connect() as db:

            await db.execute(
                """
                INSERT INTO messages
                (user_id, role, content)
                VALUES (?, ?, ?)
                """,
                (
                    user_id,
                    role,
                    content,
                ),
            )

            await db.commit()

     async def get_history(
        self,
        user_id: int,
        limit: int = 10,
    ):
        async with await self.connect() as db:

            cursor = await db.execute(
                """
                SELECT role, content
                FROM messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    user_id,
                    limit,
                ),
            )

            rows = await cursor.fetchall()
            rows.reverse()

            return rows

    async def clear_history(
        self,
        user_id: int,
    ):
        async with await self.connect() as db:

            await db.execute(
                """
                DELETE FROM messages
                WHERE user_id = ?
                """,
                (user_id,),
            )

            await db.commit()

    async def save_memory(
        self,
        user_id: int,
        key: str,
        value: str,
    ):
        async with await self.connect() as db:

            cursor = await db.execute(
                """
                SELECT id
                FROM memories
                WHERE user_id = ?
                AND key = ?
                """,
                (
                    user_id,
                    key,
                ),
            )

            exists = await cursor.fetchone()

            if exists:

                await db.execute(
                    """
                    UPDATE memories
                    SET value = ?
                    WHERE user_id = ?
                    AND key = ?
                    """,
                    (
                        value,
                        user_id,
                        key,
                    ),
                )

            else:

                await db.execute(
                    """
                    INSERT INTO memories
                    (user_id, key, value)
                    VALUES (?, ?, ?)
                    """,
                    (
                        user_id,
                        key,
                        value,
                    ),
                )

            await db.commit()

    async def get_memories(
        self,
        user_id: int,
    ):
        async with await self.connect() as db:

            cursor = await db.execute(
                """
                SELECT key, value
                FROM memories
                WHERE user_id = ?
                """,
                (user_id,),
            )

            return await cursor.fetchall()


database = Database()
            
