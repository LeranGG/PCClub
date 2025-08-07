
import logging, asyncio, datetime
from aiogram import Bot, Dispatcher
from conf import TOKEN, ADMIN, PCCLUB
from command import commands_router
from callback import callback_router
from fsm import fsm_router
from funcs import get_db_pool
from test import taxes, ads
from commands import *
from callbacks import *


logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

bot = Bot(token=TOKEN)

dp = Dispatcher()

routers = [
    commands_router,
    callback_router,
    fsm_router,
    cmd_upgrades_router,
    cmd_franchise_router,
    cmd_games_router,
    cmd_economy_router,
    cmd_admin_router,
    cb_network_router,
    cb_economy_router
]


async def every_10_min():
    while True:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            users = await conn.fetch('SELECT userid, bal, income, network, all_wallet, premium, net_inc, taxes, room, max_bal FROM stats')
            for user in users:
                for taxe in taxes:
                    if user[8] == taxe[0] and user[7] >= taxe[1]:
                        pass
                    else:
                        bufs = await conn.fetchrow('SELECT upgrade_Internet, upgrade_devices, upgrade_interior, upgrade_minibar, upgrade_service FROM stats WHERE userid = $1', user[0])
                        user_ad = await conn.fetchrow('SELECT * FROM ads WHERE userid = $1 ORDER BY dt DESC LIMIT 1', user[0])
                        i = user[2]
                        admin = 0
                        prem = 0
                        summ = 0
                        ad_inc = 0

                        for buf in bufs:
                            summ += i/100*buf

                        for ad in ads:
                            if user_ad != None and user_ad[1] == ad[0] and user_ad[3] + datetime.timedelta(hours=ad[4]+ad[5]) > datetime.datetime.today():
                                ad_inc = i/100*user_ad[2]

                        if user[5] > datetime.datetime.today():
                            prem = i/2
                        if user[0] == ADMIN[1]:
                            admin = i/100*5
                        i = i + admin + prem + summ + ad_inc
                        await conn.execute('UPDATE stats SET bal = $1, all_wallet = $2, taxes = $3 WHERE userid = $4', i+user[1], i+user[4], user[7]+i/100*5, user[0])
                        if user[1]+i > user[9]:
                            await conn.execute('UPDATE stats SET max_bal = bal')
                        if user[3] != None:
                            network = await conn.fetchrow('SELECT income FROM networks WHERE owner_id = $1', user[3])
                            await conn.execute('UPDATE networks SET income = $1 WHERE owner_id = $2', network[0]+i, user[3])
                            await conn.execute('UPDATE stats SET net_inc = $1 WHERE userid = $2', user[6]+i, user[0])
        await asyncio.sleep(600)

async def every_day():
    while True:
        dt = f'{datetime.datetime.today()}'
        if dt[11:19] == '00:00:00':
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                await conn.execute('UPDATE stats SET bonus = 1')
            await asyncio.sleep(1)
        await asyncio.sleep(0.1)


async def every_week():
    while True:
        dt = f'{datetime.datetime.today()}'
        if dt[11:19] == '16:00:00' and datetime.datetime.today().weekday() == 6:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                bal = await conn.fetch('SELECT name, income FROM networks WHERE owner_id != $1 ORDER BY income DESC LIMIT 10', ADMIN[0])
                text = ''
                num = 1
                text += '🔥 Итоги за неделю по доходу франшиз:\n'
                for user in bal:
                    text += f'\n{num}) {user[0]} - {user[1]}$'
                    num += 1
                text += '\n\n👑 Премиум был начислен для топ 5 и 2 случайных пользователей состоящих в топ 5 франшизах.'
                await bot.send_message(PCCLUB, text)
                top = await conn.fetch('SELECT * FROM networks WHERE owner_id != $1 ORDER BY income DESC LIMIT 5', ADMIN[0])
                for network in top:
                    users = await conn.fetch('SELECT userid, premium FROM stats WHERE network = $1 ORDER BY net_inc DESC LIMIT 5', network[1])
                    for user in users:
                        if user[1] < datetime.datetime.today():
                            await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', datetime.datetime.today()+datetime.timedelta(days=1), user[0])
                        else:
                            await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', user[1]+datetime.timedelta(days=1), user[0])
                    
                    random_users = await conn.fetch('''
                        SELECT userid, premium FROM stats 
                        WHERE network = $1 AND userid NOT IN (
                            SELECT userid FROM stats WHERE network = $1 ORDER BY net_inc DESC LIMIT 5
                        )
                        ORDER BY RANDOM() LIMIT 2
                    ''', network[1])
                    
                    if random_users != None:
                        for user in random_users:
                            if user[1] < datetime.datetime.today():
                                await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', datetime.datetime.today()+datetime.timedelta(days=1), user[0])
                            else:
                                await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', user[1]+datetime.timedelta(days=1), user[0])
                await conn.execute('UPDATE networks SET income = 0')
                await conn.execute('UPDATE stats SET net_inc = 0, tickets = tickets + 1')
        await asyncio.sleep(1)


async def main():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        pass
    
    for router in routers:
        dp.include_router(router)

    asyncio.create_task(every_10_min())
    asyncio.create_task(every_day())
    asyncio.create_task(every_week())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, polling_timeout=20)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')