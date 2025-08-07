
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
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrades')
        stats = await conn.fetchrow('SELECT upgrade_Internet, upgrade_devices, upgrade_interior, upgrade_minibar, upgrade_service FROM stats WHERE userid = $1', message.from_user.id)
        text = '🔧 Улучшения:'
        els = [[0, 'Интернет', 'upgrade_Internet'],
               [1, 'Девайсы', 'upgrade_devices'],
               [2, 'Интерьер', 'upgrade_interior'],
               [3, 'Мини-бар', 'upgrade_minibar'],
               [4, 'Сервис', 'upgrade_service']
        ]
        for el in els:
            el.append(stats[el[0]])
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
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_Internet')
        stats = await conn.fetchrow('SELECT bal, upgrade_Internet FROM stats WHERE userid = $1', message.from_user.id)
        for upg in upgrade:
            if upg[0] == stats[1]+1:
                if stats[1] != 10:
                    if stats[0] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_Internet = $1 WHERE userid = $2', stats[1]+1, message.from_user.id)
                        await conn.execute('UPDATE stats SET bal = $1 WHERE userid = $2', stats[0]-upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили интернет')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')


@cmd_upgrades_router.message(Command('upgrade_devices'))
async def cmd_upgrade_devices(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_devices')
        stats = await conn.fetchrow('SELECT bal, upgrade_devices FROM stats WHERE userid = $1', message.from_user.id)
        for upg in upgrade:
            if upg[0] == stats[1]+1:
                if stats[1] != 10:
                    if stats[0] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_devices = $1 WHERE userid = $2', stats[1]+1, message.from_user.id)
                        await conn.execute('UPDATE stats SET bal = $1 WHERE userid = $2', stats[0]-upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили девайсы')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')


@cmd_upgrades_router.message(Command('upgrade_interior'))
async def cmd_upgrade_interior(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_interior')
        stats = await conn.fetchrow('SELECT bal, upgrade_interior FROM stats WHERE userid = $1', message.from_user.id)
        for upg in upgrade:
            if upg[0] == stats[1]+1:
                if stats[1] != 10:
                    if stats[0] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_interior = $1 WHERE userid = $2', stats[1]+1, message.from_user.id)
                        await conn.execute('UPDATE stats SET bal = $1 WHERE userid = $2', stats[0]-upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили интерьер')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')


@cmd_upgrades_router.message(Command('upgrade_minibar'))
async def cmd_upgrade_minibar(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_minibar')
        stats = await conn.fetchrow('SELECT bal, upgrade_minibar FROM stats WHERE userid = $1', message.from_user.id)
        for upg in upgrade:
            if upg[0] == stats[1]+1:
                if stats[1] != 10:
                    if stats[0] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_minibar = $1 WHERE userid = $2', stats[1]+1, message.from_user.id)
                        await conn.execute('UPDATE stats SET bal = $1 WHERE userid = $2', stats[0]-upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили мини-бары')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')


@cmd_upgrades_router.message(Command('upgrade_service'))
async def cmd_upgrade_service(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_upgrade_service')
        stats = await conn.fetchrow('SELECT bal, upgrade_service FROM stats WHERE userid = $1', message.from_user.id)
        for upg in upgrade:
            if upg[0] == stats[1]+1:
                if stats[1] != 10:
                    if stats[0] >= upg[1]:
                        await conn.execute('UPDATE stats SET upgrade_service = $1 WHERE userid = $2', stats[1]+1, message.from_user.id)
                        await conn.execute('UPDATE stats SET bal = $1 WHERE userid = $2', stats[0]-upg[1], message.from_user.id)
                        await message.answer('✅ Вы успешно улучшили сервис')
                    else:
                        await message.answer('❌ У вас недостаточно средств')
                else:
                    await message.answer('⚠️ Вы достигли максимального уровня')
