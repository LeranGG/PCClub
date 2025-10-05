# tasks.py

import datetime, aiocron
from conf import ADMIN, TOKEN
from funcs.funcs import get_db_pool
from test import taxes, ads


def calculate_upgrades_income(base_income, upgrades):
    return sum(base_income / 100 * upgrade for upgrade in upgrades)


def calculate_ad_income(base_income, user_ad):
    if user_ad:
        for ad in ads:
            ad_id, ad_val, ad_start, ad_hours, ad_extra1, ad_extra2 = ad
            if user_ad[1] == ad_id and user_ad[3] + datetime.timedelta(hours=ad_hours + ad_extra2) > datetime.datetime.now():
                return base_income / 100 * user_ad[2]
    return 0


async def process_user(user, conn):
    userid, bal, income, network, all_wallet, premium, taxes_value, room, max_bal = user

    for taxe in taxes:
        if room == taxe[0] and taxes_value >= taxe[1]:
            return

    upgrades = await conn.fetchrow(
        'SELECT upgrade_Internet, upgrade_devices, upgrade_interior, upgrade_minibar, upgrade_service '
        'FROM stats WHERE userid = $1', userid
    )
    user_ad = await conn.fetchrow('SELECT * FROM ads WHERE userid = $1 ORDER BY dt DESC LIMIT 1', userid)

    base_income = income
    admin_bonus = 0
    premium_bonus = 0
    upgrades_bonus = calculate_upgrades_income(base_income, upgrades)
    ad_bonus = calculate_ad_income(base_income, user_ad)

    if premium and premium > datetime.datetime.now():
        premium_bonus = base_income / 2

    if userid in ADMIN and TOKEN != '7391256097:AAGVbvFUMW5ShfffjsPFFvFl9QONZ2kJbu8':
        admin_bonus = base_income / 100 * 5

    total_income = base_income + admin_bonus + premium_bonus + upgrades_bonus + ad_bonus

    await conn.execute(
        'UPDATE stats SET bal = bal + $1, all_wallet = all_wallet + $1, taxes = taxes + $2 WHERE userid = $3',
        total_income, total_income / 100 * 5, userid
    )
    await conn.execute('UPDATE stats SET max_bal = GREATEST(max_bal, bal) WHERE userid = $1', userid)

    if network:
        await conn.execute('UPDATE networks SET income = income + $1 WHERE owner_id = $2', total_income, network)
        await conn.execute('UPDATE stats SET net_inc = net_inc + $1 WHERE userid = $2', total_income, userid)


async def every_10_min(conn):
    users = await conn.fetch(
        'SELECT userid, bal, income, network, all_wallet, premium, taxes, room, max_bal FROM stats'
    )
    for user in users:
        await process_user(user, conn)


@aiocron.crontab('*/10 * * * *')
async def cron_every_10_min():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await every_10_min(conn)
