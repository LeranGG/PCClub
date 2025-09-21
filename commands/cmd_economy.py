
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
        await add_action(message.from_user.id, 'cmd_pay_taxes')
        await message.answer(f'Налоги увеличиваются на 5% от вашего заработка.\nВаша задолженность: {user[1]}$ / {max_taxes}$\n❗ Если налоги достигнут максимума, то ваш доход будет заморожен!\nУплатить налоги: /pay_taxes')


@cmd_economy_router.message(Command('pay_taxes'))
async def cmd_pay_taxes(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, taxes, bal FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_pay_taxes')
        if user[2] >= user[1]:
            await conn.execute('UPDATE stats SET bal = bal - taxes, taxes = 0 WHERE userid = $2', message.from_user.id)
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
        user = await conn.fetchrow('SELECT name, bal, income, pc FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_sell')
        text = message.text.split('_', 1)
        text = text[1].split(' ', 1)
        if len(text) == 1:
            text.append('1')
        text[0] = text[0].split('@PCClub_sBOT')[0]
        text[1] = text[1].split('@PCClub_sBOT')[0]
        ctids = await conn.fetch('SELECT ctid FROM pc WHERE userid = $1 AND lvl = $2', message.from_user.id, text[0])
        if text[1] == 'max':
            text[1] = str(ctids)
        if (len(text) == 2 and text[0].isdigit() and text[1].isdigit()) or (len(text) == 1 and text[0].isdigit()):
            pcs = await conn.fetchrow('SELECT * FROM pc WHERE userid = $1 AND lvl = $2', message.from_user.id, int(text[0]))
            for pc in prices:
                if int(text[0]) == pc[0]:
                    if pcs != None:
                        ctids = await conn.fetch('SELECT ctid FROM pc WHERE userid = $1 AND lvl = $2 LIMIT $3', message.from_user.id, pc[0], int(text[1]))
                        if len(ctids) == int(text[1]):
                            inc = 0
                            for ctid in ctids:
                                comp = Decimal(str(pc[1]))
                                await conn.execute('DELETE FROM pc WHERE ctid = $1', ctid[0])
                                await conn.execute('UPDATE stats SET bal = bal + $1, income = income - $2, pc = pc - 1 WHERE userid = $3', pc[2]//2, comp, message.from_user.id)
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
        user = await conn.fetchrow('SELECT name, bal, room, pc, income FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_buy')
        text = message.text.split('_', 1)
        text = text[1].split(' ', 1)
        if len(text) == 1:
            text.append('1')
        text[0] = text[0].split('@PCClub_sBOT')[0]
        text[1] = text[1].split('@PCClub_sBOT')[0]
        if text[1] == 'max':
            text[1] = user[2]*5 - user[3]
            while user[1] < prices[int(int(text[0])-1)][2]*int(text[1]):
                text[1] -= 1
            text[1] = str(text[1])
        if (len(text) == 2 and text[0].isdigit() and text[1].isdigit()) or (len(text) == 1 and text[0].isdigit()):
            for el in prices:
                if int(text[0]) == el[0] and user[1] >= el[2]*int(text[1]) and user[3]+int(text[1]) <= user[2]*5 and user[2] >= int(text[0]):
                    pc_inc = Decimal(str(el[1]))
                    await conn.execute('UPDATE stats SET bal = bal - $1, pc = pc + $2, income = income + $3, all_pcs = all_pcs + $4 WHERE userid = $5', el[2]*int(text[1]), int(text[1]), pc_inc*int(text[1]), int(text[1]), message.from_user.id)
                    for i in range(0, int(text[1])):
                        await conn.execute('INSERT INTO pc (userid, lvl, income) VALUES ($1, $2, $3)', message.from_user.id, int(text[0]), pc_inc)
                    await message.answer(f'✅ Вы успешно купили x{text[1]} Компьютер {text[0]} ур. за {el[2]*int(text[1])}$')
                elif int(text[0]) == el[0] and user[1] < el[2]*int(text[1]):
                    await message.answer('❌ У вас не достаточно средств!')
                elif int(text[0]) == el[0] and user[3]+int(text[1]) > user[2]*5:
                    await message.answer('❌ У вас не хватает места. Чтобы увеличить количество мест улучшите комнату!')
                elif int(text[0]) == el[0] and user[2] < int(text[0]):
                    await message.answer('❌ Этот компьютер вам не доступен!')
        else:
            await message.answer('⚠ Команду надо использовать в формате:\n /buy_(уровень компьютера*) (количество)')
