
import asyncpg
from conf import PASSWORD

db_pool = None

async def get_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = await asyncpg.create_pool(
            user='postgres',
            password=PASSWORD,
            database='PCClub',
            host='localhost',
            port=5432
        )
    return db_pool


async def update_data(username, userid):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute('UPDATE stats SET username = $1 WHERE userid = $2', username, userid)

async def add_action(user, action):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute('INSERT INTO actions (userid, action) VALUES ($1, $2)', user, action)

        