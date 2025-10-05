# weekly_tasks.py
import asyncio
import datetime
import aiocron
from aiogram import Bot
from funcs.funcs import get_db_pool
from conf import ADMIN, PCCLUB, TOKEN

bot = Bot(token=TOKEN)

async def process_weekly_results():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        bal = await conn.fetch(
            'SELECT name, income FROM networks WHERE owner_id != $1 ORDER BY income DESC LIMIT 10',
            ADMIN[0]
        )
        text = format_top10_message(bal)
        await bot.send_message(PCCLUB, text)

        await reward_premium(conn)

        await conn.execute('UPDATE networks SET income = 0')
        await conn.execute('UPDATE stats SET net_inc = 0')


def format_top10_message(bal):
    text = '🔥 Итоги за неделю по доходу франшиз:\n'
    for num, user in enumerate(bal, start=1):
        text += f'\n{num}) {user[0]} - {user[1]}$'
    text += '\n\n👑 Премиум был начислен для топ 5 и 2 случайных пользователей состоящих в топ 5 франшизах.'
    return text


async def reward_premium(conn):
    top = await conn.fetch(
        'SELECT * FROM networks WHERE owner_id != $1 ORDER BY income DESC LIMIT 5',
        ADMIN[0]
    )
    for network in top:
        users = await conn.fetch(
            'SELECT userid, premium FROM stats WHERE network = $1 ORDER BY net_inc DESC LIMIT 5',
            network[1]
        )
        await extend_premium(conn, users)

        random_users = await conn.fetch('''
            SELECT userid, premium FROM stats 
            WHERE network = $1 AND userid NOT IN (
                SELECT userid FROM stats WHERE network = $1 ORDER BY net_inc DESC LIMIT 5
            )
            ORDER BY RANDOM() LIMIT 2
        ''', network[1])
        await extend_premium(conn, random_users)


async def extend_premium(conn, users):
    for user in users:
        if user[1] < datetime.datetime.now():
            new_premium = datetime.datetime.now() + datetime.timedelta(days=1)
        else:
            new_premium = user[1] + datetime.timedelta(days=1)
        await conn.execute(
            'UPDATE stats SET premium = $1 WHERE userid = $2',
            new_premium, user[0]
        )


@aiocron.crontab('0 19 * * 0')
async def cron_every_week():
    await process_weekly_results()
