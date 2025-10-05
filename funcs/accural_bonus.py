import aiocron
from funcs.funcs import get_db_pool


@aiocron.crontab('0 0 * * *')
async def daily_bonus():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute('UPDATE stats SET bonus = 1')
