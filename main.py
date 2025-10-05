
import asyncio
from aiogram import Bot, Dispatcher
from conf import TOKEN
from callback import callback_router
from fsm import fsm_router
from commands import *
from callbacks import *
from funcs.results_franchises import cron_every_week
from funcs.accrual_income import cron_every_10_min
from funcs.accural_bonus import daily_bonus
from funcs.logging import logger  # импорт настроенного логгера
from funcs.funcs import get_db_pool


bot = Bot(token=TOKEN)

dp = Dispatcher()

routers = [
    callback_router,
    fsm_router,
    cmd_upgrades_router,
    cmd_franchise_router,
    cmd_games_router,
    cmd_economy_router,
    cmd_admin_router,
    cmd_user_router,
    cb_network_router,
    cb_economy_router,
    cb_games_router,
    cb_donate_router
]


async def main():
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        pass
    
    for router in routers:
        dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, polling_timeout=20)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')