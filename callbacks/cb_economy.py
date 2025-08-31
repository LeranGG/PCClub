
import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from funcs import get_db_pool, update_data, add_action
from test import update, prices, upgrade, ads
from random import randint
from decimal import Decimal, getcontext


cb_economy_router = Router()

getcontext().prec = 50


@cb_economy_router.callback_query(F.data.startswith('shop_pc'))
async def cb_shop_pc(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, room FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_shop_pc')
        num = 0
        text = '🖥️ Доступные компьютеры:\n\n'
        for pc in reversed(prices):
            if user[1] >= pc[0] and num <= 5:
                text += f'Компьютер {pc[0]} ур. Доход: {pc[1]}$ / 10 мин.\nЦена: {pc[2]}$ Купить: /buy_{pc[0]}\n\n'
                num += 1
        text += f'🛒 Купить компьютер:\n/buy_(уровень компьютера*) (количество)'
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔙 Назад', callback_data=f'shop_{callback.from_user.id}')]
        ])
        await callback.message.edit_text(text, reply_markup=markup)
            

@cb_economy_router.callback_query(F.data.startswith('shop_ads'))
async def cb_shop_ads(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_shop_ads')
        text = '📢 Какую рекламу вы хотите купить?\n'
        markup = InlineKeyboardMarkup(inline_keyboard=[])
        for ad in ads:
            text += f'\n{ad[0]}) {ad[1]}. Цена: {ad[2]}$\nБонус: +{ad[3]}%. Срок/откат: {ad[4]}/{ad[5]} ч.\n'
        for i in range(0, len(ads), 3):
            row_ads = ads[i:i+3]
            row_buttons = []
            for ad in row_ads:
                row_buttons.append(InlineKeyboardButton(text=f'{ad[0]}) {ad[1][0]}', callback_data=f'buy_ad{ad[0]}_{callback.from_user.id}'))
            markup.inline_keyboard.append(row_buttons)
        markup.inline_keyboard.append([InlineKeyboardButton(text='🔙 Назад', callback_data=f'shop_{callback.from_user.id}')])
        await callback.message.edit_text(text, reply_markup=markup)


@cb_economy_router.callback_query(F.data.startswith('buy_ad'))
async def cb_buy_ad(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, bal FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_buy_ad')
        user_ad = await conn.fetchrow('SELECT * FROM ads WHERE userid = $1 ORDER BY dt DESC LIMIT 1', callback.from_user.id)
        success = 0
        for ad in ads:
            if user_ad == None or user_ad[1] == ad[0] and user_ad[3] + datetime.timedelta(hours=ad[4]+ad[5]) < datetime.datetime.today():
                success = 1
        if success != 1:
            await callback.message.edit_text(f'⚠️ Вы недавно уже покупали рекламу')
            return
        for ad in ads:
            if ad[0] == int(callback.data[6]):
                if user[1] >= ad[2]:
                    await conn.execute('UPDATE stats SET bal = bal - $1 WHERE userid = $2', ad[2], callback.from_user.id)
                    await conn.execute('INSERT INTO ads (userid, percent, num) VALUES ($1, $2, $3)', callback.from_user.id, ad[3], ad[0])
                    await callback.message.edit_text(f'✅ Вы успешно купили рекламу {ad[1]}')
                else:
                    await callback.message.edit_text(f'❌ Недостаточно средств')


@cb_economy_router.callback_query(F.data.startswith('shop_room'))
async def cb_shop_room(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, room FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_shop_room')
        markup1 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='⏫ Улучшить', callback_data=f'update_room_{callback.from_user.id}')],
            [InlineKeyboardButton(text='🔙 Назад', callback_data=f'shop_{callback.from_user.id}')]
        ])
        markup2 = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔙 Назад', callback_data=f'shop_{callback.from_user.id}')]
        ])
        for el in update:
            if user[1]+1 == el[0]:
                await callback.message.edit_text(f'Уровень вашей комнаты: {user[1]}\nМинимальный доход для улучшения: {el[2]}$\nЦена улучшения: {el[1]}$', reply_markup=markup1)
                return
        if user[1] == 50:
            await callback.message.edit_text(f'Уровень вашей комнаты: {user[1]}\n❇️ Максимальный!', reply_markup=markup2)


@cb_economy_router.callback_query(F.data.startswith('shop_upgrade'))
async def cb_shop_upgrade(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, upgrade_Internet, upgrade_devices, upgrade_interior, upgrade_minibar, upgrade_service FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_shop_upgrade')
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
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔙 Назад', callback_data=f'shop_{callback.from_user.id}')]
        ])
        await callback.message.edit_text(text, reply_markup=markup)


@cb_economy_router.callback_query(F.data.startswith('update_room'))
async def cb_update_room(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, room, bal, income FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_update_room')
        for el in update:
            b = Decimal(str(user[2]))
            if user[2] >= el[1] and user[1]+1 == el[0] and user[3] >= el[2]:
                await conn.execute('UPDATE stats SET bal = bal - $1, room = room + 1 WHERE userid = $2', el[1], callback.from_user.id)
                await callback.message.edit_text('✅ Вы успешно прокачали комнату')
                if el[0] == 2:
                    ref = await conn.fetchval('SELECT ref FROM stats WHERE userid = $1', callback.from_user.id)
                    if ref != None and ref > 0:
                        prem = await conn.fetchval('SELECT premium FROM stats WHERE userid = $1', ref)
                        if prem > datetime.datetime.today():
                            await conn.execute('UPDATE stats SET premium = premium + $1 WHERE userid = $2', datetime.timedelta(hours=12), ref)
                        else:
                            await conn.execute('UPDATE stats SET premium = NOW() + $1 WHERE userid = $2', datetime.timedelta(hours=12), ref)
            elif user[2] < el[1] and user[1]+1 == el[0]:
                await callback.message.edit_text('❌ У вас не хватает $')
            elif user[3] < el[2] and user[1]+1 == el[0]:
                await callback.message.edit_text(f'❌ У вас недостаточно дохода, нужно: {el[2]}')
    

@cb_economy_router.callback_query(F.data.startswith('bonus'))
async def cb_bonus(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, bonus, bal, income, all_wallet, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_bonus')
        income = await conn.fetchrow('SELECT income FROM networks WHERE owner_id = $1', user[5])
        i = Decimal(str(user[3]))
        if user[1] == 1:
            x = 5
            percent = randint(1, 100)
            if percent <= 5:
                x = 20
            elif percent <= 15:
                x = 15
            elif percent <= 30:
                x = 10
            elif percent <= 50:
                x = 6
            total = i * x * 6
            if total <= 150000:
                if income != None:
                    await conn.execute('UPDATE networks SET income = income + $1 WHERE owner_id = $2', total, user[5])
                await conn.execute('UPDATE stats SET bonus = 0, bal = bal + $1, all_wallet = all_wallet + $1 WHERE userid = $2', total, callback.from_user.id)
                await callback.message.edit_text(f'✨ Вы успешно получили {total}$')
            else:
                total = 150000
                if income != None:
                    await conn.execute('UPDATE networks SET income = income + $1 WHERE owner_id = $2', total, user[5])
                await conn.execute('UPDATE stats SET bonus = 0, bal = bal + $1, all_wallet = all_wallet + $1 WHERE userid = $2', total, callback.from_user.id)
                await callback.message.edit_text(f'✨ Вы успешно получили {total}$')
        else:
            await callback.message.edit_text('🕛 Ежедневный бонус ещё не доступен, он обновляется каждый день в 00:00 по МСК')


@cb_economy_router.callback_query(F.data.startswith('shop'))
async def cb_shop(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_shop')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🖥 Компьютеры', callback_data=f'shop_pc_{callback.from_user.id}')],
            [InlineKeyboardButton(text='⏫ Комната', callback_data=f'shop_room_{callback.from_user.id}')],
            [InlineKeyboardButton(text='🔧 Улучшения', callback_data=f'shop_upgrade_{callback.from_user.id}')],
            [InlineKeyboardButton(text='📢 Реклама', callback_data=f'shop_ads_{callback.from_user.id}')]
        ])
        await callback.message.edit_text    ('🛒 PC Club Shop\nВыберите раздел:', reply_markup=markup)
