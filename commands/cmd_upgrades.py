
from aiogram.filters import Command
from aiogram.types import Message
from funcs import get_db_pool, update_data, add_action
from test import upgrade
from aiogram import Router


cmd_upgrades_router = Router()


@cmd_upgrades_router.message(Command('upgrades'))
async def cmd_upgrades(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, upgrade_Internet, upgrade_devices, upgrade_interior, upgrade_minibar, upgrade_service FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrades')
        text = '🔧 Улучшения:'
        els = [[1, 'Интернет', 'upgrade_Internet'],
               [2, 'Девайсы', 'upgrade_devices'],
               [3, 'Интерьер', 'upgrade_interior'],
               [4, 'Мини-бар', 'upgrade_minibar'],
               [5, 'Сервис', 'upgrade_service']
        ]
        for el in els:
            el.append(user[el[0]])
        for el in els:
            for upg in upgrade:
                if el[3]+1 == upg[0]:
                    if upg[0] == 11:
                        text += f'\n\n{el[1]}: +{el[3]}%. Максимум'
                    else:
                        text += f'\n\n{el[1]}: +{el[3]}%. Цена: {upg[1]}$\nУлучшить: /{el[2]}'
        await message.answer(text)


@cmd_upgrades_router.message(Command('upgrade_Internet'))
async def cmd_upgrade_Internet(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, bal, upgrade_Internet FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_Internet')
        for upg in upgrade:
            if upg[0] == user[2]+1:
                if user[2] != 10:
                    if user[1] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_Internet = upgrade_Internet + 1, bal = bal - $1 WHERE userid = $2', upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили интернет')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')


@cmd_upgrades_router.message(Command('upgrade_devices'))
async def cmd_upgrade_devices(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, bal, upgrade_devices FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_devices')
        for upg in upgrade:
            if upg[0] == user[2]+1:
                if user[2] != 10:
                    if user[1] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_devices = upgrade_devices + 1, bal = bal - $1 WHERE userid = $2', upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили девайсы')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')


@cmd_upgrades_router.message(Command('upgrade_interior'))
async def cmd_upgrade_interior(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, bal, upgrade_interior FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_interior')
        for upg in upgrade:
            if upg[0] == user[2]+1:
                if user[2] != 10:
                    if user[1] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_interior = upgrade_interior + 1, bal = bal - $1 WHERE userid = $2', upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили интерьер')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')


@cmd_upgrades_router.message(Command('upgrade_minibar'))
async def cmd_upgrade_minibar(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, bal, upgrade_minibar FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_minibar')
        for upg in upgrade:
            if upg[0] == user[2]+1:
                if user[2] != 10:
                    if user[1] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_minibar = upgrade_minibar + 1, bal = bal - $1 WHERE userid = $2', upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили мини-бары')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')


@cmd_upgrades_router.message(Command('upgrade_service'))
async def cmd_upgrade_service(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, bal, upgrade_service FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_service')
        for upg in upgrade:
            if upg[0] == user[2]+1:
                if user[2] != 10:
                    if user[1] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_service = upgrade_service + 1, bal = bal - $1 WHERE userid = $2', upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили сервис')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')
