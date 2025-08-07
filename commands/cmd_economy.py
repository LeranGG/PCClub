
from aiogram.filters import Command
from funcs import get_db_pool, update_data, add_action
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Router, F
from test import prices, taxes
from decimal import Decimal, getcontext


cmd_economy_router = Router()

getcontext().prec = 50


@cmd_economy_router.message(F.text == '🛒 Магазин')
async def msg_shop(message: Message):
    await cmd_shop(message)


@cmd_economy_router.message(Command('taxes'))
async def cmd_taxes(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, taxes, room FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        for taxe in taxes:
            if user[2] == taxe[0]:
                max_taxes = taxe[1]
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_taxes')
        await message.answer(f'Налоги увеличиваются на 5% от вашего заработка.\nВаша задолженность: {user[1]}$ / {max_taxes}$\n❗ Если налоги достигнут максимума, то ваш доход будет заморожен!\nУплатить налоги: /pay_taxes')


@cmd_economy_router.message(Command('pay_taxes'))
async def cmd_taxes(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, taxes, bal FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        if user[2] >= user[1]:
            await conn.execute('UPDATE stats SET bal = $1 WHERE userid = $2', user[2] - user[1], message.from_user.id)
            await conn.execute('UPDATE stats SET taxes = $1 WHERE userid = $2', 0, message.from_user.id)
            await message.answer(f'✅ Вы успешно уплатили все налоги. Общая сумма составила {user[1]}$')
        else:
            await message.answer('❌ У вас недостаточно средств')


@cmd_economy_router.message(Command('shop'))
async def cmd_shop(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_shop')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🖥 Компьютеры', callback_data=f'shop_pc_{message.from_user.id}')],
            [InlineKeyboardButton(text='⏫ Комната', callback_data=f'shop_room_{message.from_user.id}')],
            [InlineKeyboardButton(text='🔧 Улучшения', callback_data=f'shop_upgrade_{message.from_user.id}')],
            [InlineKeyboardButton(text='📢 Реклама', callback_data=f'shop_ads_{message.from_user.id}')]
        ])
        await message.answer('🛒 PC Club Shop\nВыберите раздел:', reply_markup=markup)


@cmd_economy_router.message(F.text[:6] == '/sell_')
async def cmd_sell(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_sell')
        text = message.text.split('@PCClub_sBOT', 1)[0]
        text = text.split('_', 1)
        text = text[1].split(' ', 1)
        if (len(text) == 2 and text[0].isdigit() and text[1].isdigit()) or (len(text) == 1 and text[0].isdigit()):
            pcs = await conn.fetchrow('SELECT * FROM pc WHERE userid = $1 AND lvl = $2', message.from_user.id, int(text[0]))
            for pc in prices:
                if int(text[0]) == pc[0]:
                    if pcs != None:
                        if len(text) == 1:
                            text.append('1')
                        ctids = await conn.fetch('SELECT ctid FROM pc WHERE userid = $1 AND lvl = $2 LIMIT $3', message.from_user.id, pc[0], int(text[1]))
                        if len(ctids) == int(text[1]):
                            inc = 0
                            for ctid in ctids:
                                stats = await conn.fetchrow('SELECT bal, income, pc FROM stats WHERE userid = $1', message.from_user.id)
                                comp = Decimal(str(pc[1]))
                                await conn.execute('DELETE FROM pc WHERE ctid = $1', ctid[0])
                                await conn.execute('UPDATE stats SET bal = $1, income = $2, pc = $3 WHERE userid = $4', stats[0]+pc[2]//2, stats[1]-comp, stats[2]-1, message.from_user.id)
                                inc += pc[2]//2
                            await message.answer(f'✅ Вы успешно продали x{text[1]} Компьютер {pc[0]} ур. за {inc}$')
                        else:
                            await message.answer('❌ У вас не хватает этих компьютеров')
                    else:
                        await message.answer('❌ У вас в наличии нет этого компьютера')
        else:
            await message.answer('⚠ Команду надо использовать в формате:\n /sell_(уровень компьютера*) (количество)')


@cmd_economy_router.message(F.text.startswith('/buy_'))
async def cmd_buy(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_buy')
        text = message.text.split('@PCClub_sBOT', 1)[0]
        text = text.split('_', 1)
        text = text[1].split(' ', 1)
        if (len(text) == 2 and text[0].isdigit() and text[1].isdigit()) or (len(text) == 1 and text[0].isdigit()):
            stats = await conn.fetchrow('SELECT bal, room, pc, income FROM stats WHERE userid = $1', message.from_user.id)
            for el in prices:
                if len(text) == 1:
                    text.append('1')
                if int(text[0]) == el[0] and stats[0] >= el[2]*int(text[1]) and stats[2]+int(text[1]) <= stats[1]*5 and stats[1] >= int(text[0]):
                    bal = Decimal(str(stats[0]))
                    income = Decimal(str(stats[3]))
                    pc_inc = Decimal(str(el[1]))
                    await conn.execute('UPDATE stats SET bal = $1, pc = $2, income = $3, all_pcs = all_pcs + $4 WHERE userid = $5', bal-el[2]*int(text[1]), stats[2]+int(text[1]), income+pc_inc*int(text[1]), int(text[1]), message.from_user.id)
                    for i in range(0, int(text[1])):
                        await conn.execute('INSERT INTO pc (userid, lvl, income) VALUES ($1, $2, $3)', message.from_user.id, int(text[0]), pc_inc)
                    await message.answer(f'✅ Вы успешно купили x{text[1]} Компьютер {text[0]} ур. за {el[2]*int(text[1])}$')
                elif int(text[0]) == el[0] and stats[0] < el[2]*int(text[1]):
                    await message.answer('❌ У вас не достаточно средств!')
                elif int(text[0]) == el[0] and stats[2]+int(text[1]) > stats[1]*5:
                    await message.answer('❌ У вас не хватает места. Чтобы увеличить количество мест улучшите комнату!')
                elif int(text[0]) == el[0] and stats[1] < int(text[0]):
                    await message.answer('❌ Этот компьютер вам не доступен!')
        else:
            await message.answer('⚠ Команду надо использовать в формате:\n /buy_(уровень компьютера*) (количество)')
