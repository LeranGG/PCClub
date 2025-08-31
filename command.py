
import datetime
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, CommandStart
from aiogram import Router, Bot, F
from conf import ADMIN, TOKEN
from decimal import Decimal, getcontext
from funcs import get_db_pool, update_data, add_action
from test import prices, taxes, ads
from aiogram.fsm.context import FSMContext
from fsm import Rename

bot = Bot(token=TOKEN)

getcontext().prec = 50

commands_router = Router()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🖥 ПК в наличии'), KeyboardButton(text='👤 Профиль')],
        [KeyboardButton(text='🌐 Франшизы'), KeyboardButton(text='🛒 Магазин')],
        [KeyboardButton(text='🎮 Игры'), KeyboardButton(text='🏆 Топ')],
        [KeyboardButton(text='📫 Чаты')],
        [KeyboardButton(text='👑 Донат')]
    ],
    resize_keyboard=True,
    one_time_keyboard=False
)


@commands_router.message(F.text == '👤 Профиль')
async def msg_profile(message: Message):
    await cmd_profile(message)

@commands_router.message(F.text == '🖥 ПК в наличии')
async def msg_my_pcs(message: Message):
    await cmd_my_pcs(message)

@commands_router.message(F.text == '🏆 Топ')
async def msg_top(message: Message):
    await cmd_top(message)

@commands_router.message(F.text == '👑 Донат')
async def msg_donate(message: Message):
    await cmd_donate(message)

@commands_router.message(F.text == '📫 Чаты')
async def msg_chats(message: Message):
    await cmd_chats(message)


@commands_router.message(CommandStart())
async def cmd_start(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await conn.execute('INSERT INTO stats (userid, username) VALUES ($1, $2)', message.from_user.id, message.from_user.username)
            if len(message.text) > 6:
                if message.text[7:] == '-1001680896621':
                    await bot.send_message(ADMIN[0], f'Новый пользователь: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) @{message.from_user.username} от Arizona HOT', parse_mode='markdown')
                elif int(message.text[7:]) == ADMIN[0]:
                    await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', datetime.datetime.today() + datetime.timedelta(days=14), message.from_user.id)
                    await bot.send_message(ADMIN[0], f'Новый пользователь: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) @{message.from_user.username} от тебя)', parse_mode='markdown')
                else:
                    await bot.send_message(ADMIN[0], f'Новый пользователь: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) @{message.from_user.username} от [{message.text[7:]}](tg://user?id={message.text[7:]})', parse_mode='markdown')
                await conn.execute('UPDATE stats SET ref = $1 WHERE userid = $2', int(message.text[7:]), message.from_user.id)
                await conn.execute('UPDATE stats SET tickets = tickets + 1 WHERE userid = $1', int(message.text[7:]))
            else:
                await bot.send_message(ADMIN[0], f'Новый пользователь: [{message.from_user.first_name}](tg://user?id={message.from_user.id}) @{message.from_user.username}', parse_mode='markdown')
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_start')
        if message.chat.id == message.from_user.id:
            await message.answer(f'{message.from_user.first_name}, добро пожаловать! 🖐\n\n'
                                 'С помощью этого бота ты сможешь побыть на месте владельца ПК клуба!\n'
                                 'Прокачивай свою комнату, покупай для неё компьютеры и становись лучшим в своём деле 👑\n'
                                 'Быстрее иди в магазин (/shop) и покупай свои первые компьютеры уже сейчас! 🔥', reply_markup=keyboard)
        else:
            await message.answer(f'{message.from_user.first_name}, добро пожаловать! 🖐\n\n'
                                 'С помощью этого бота ты сможешь побыть на месте владельца ПК клуба!\n'
                                 'Прокачивай свою комнату, покупай для неё компьютеры и становись лучшим в своём деле 👑\n'
                                 'Быстрее иди в магазин (/shop) и покупай свои первые компьютеры уже сейчас! 🔥')


@commands_router.message(Command('nickname'))
async def cmd_nickname(message: Message, state: FSMContext):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_nickname')
        await message.answer('📝 Введите новый никнейм или /cancel для отмены действия')
        await state.set_state(Rename.name)


@commands_router.message(Command('stats'))
async def cmd_stats(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, all_wallet, reg_day, name, all_pcs, max_bal FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_stats')
        refs = await conn.fetchval('SELECT COUNT(*) FROM stats WHERE ref = $1', message.from_user.id)
        date_time = str(user[2])
        reg_day = f'{date_time[8:10]}.{date_time[5:7]}.{date_time[0:4]}'
        await message.answer(f'📈 Статистика игрока {user[3]}:\n\n💵 Заработок за всё время: {user[1]}$\n💰 Наибольший баланс за всё время: {user[5]}\n🖥️ Куплено компьютеров за всё время: {user[4]}\n👥 Рефералы: {refs}\n📅 Дата регистрации: {reg_day}')


@commands_router.message(Command('my_pcs'))
async def cmd_my_pcs(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_my_pcs')
        text = '🖥 Это ваши компьютеры:'
        for price in prices:
            pcs = await conn.fetch('SELECT income FROM pc WHERE userid = $1 AND lvl = $2', message.from_user.id, price[0])
            total_income = 0
            total_pcs = 0
            if len(pcs) > 0:
                for pc in pcs:
                    total_pcs += 1
                    total_income += Decimal(str(pc[0]))
                text = text + f'\n\nКомпьютер {price[0]} ур. {total_pcs} шт.\nДоход: {total_income}$. Продать: /sell_{price[0]}'
        text += '\n\nЧтобы продать компьютер введите:\n/sell_(уровень компьютера*) (количество)'
        await message.answer(text)


@commands_router.message(Command('my_ad'))
async def cmd_my_ad(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_my_ad')
        user_ad = await conn.fetchrow('SELECT * FROM ads WHERE userid = $1 ORDER BY dt DESC LIMIT 1', message.from_user.id)
        if user_ad == None:
            await message.answer('⚠️ Вы еще не покупали рекламу')
        else:
            for ad in ads:
                if user_ad[1] == ad[0] and user_ad[3] + datetime.timedelta(hours=ad[4]+ad[5]) < datetime.datetime.today():
                    await message.answer('❌ В данный момент у вас нет активной рекламы')
                elif user_ad[1] == ad[0] and user_ad[3] + datetime.timedelta(hours=ad[4]) < datetime.datetime.today():
                    await message.answer(f'⏳ В данный момент у вас нет активной рекламы, но вам нужно подождать до {str(user_ad[3] + datetime.timedelta(hours=ad[4]+ad[5]))[:19]} по МСК, так как вы недавно уже брали рекламу')
                elif user_ad[1] == ad[0]:
                    await message.answer(f'📢 Это ваша реклама:\n\n{ad[1]} +{ad[3]}% к доходу\nАктивна до {str(user_ad[3] + datetime.timedelta(hours=ad[4]+ad[5]))[:19]} по МСК')


@commands_router.message(Command('ref'))
async def cmd_ref(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_ref')
        refs = await conn.fetchval('SELECT COUNT(*) FROM stats WHERE ref = $1', message.from_user.id)
        await update_data(message.from_user.username, message.from_user.id)
        await message.answer(f'👤 Твоя реферальная ссылка: https://t.me/PCClub_sBOT?start={message.from_user.id}\n\n'
                             'Отправляй её друзьями и получай бонус за каждого, кто зайдет по ней в бота и достигнет 2 уровня комнаты\n\n'
                             f'Количество твоих рефералов: {refs}\n\n'
                             'Бонус за игрока: 12 часов 👑 PREMIUM 👑, а также 25% от всех купленных рефералом донатов\n'
                             'Пока идет ивент, за каждого реферала вы получите билет-удвоитель, сразу как только он запустит игру', disable_web_page_preview=True)


@commands_router.message(Command('donate'))
async def cmd_donate(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_donate')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='1 день PREMIUM', callback_data=f'donate_1day_{message.from_user.id}')],
            [InlineKeyboardButton(text='1 неделя PREMIUM', callback_data=f'donate_1week_{message.from_user.id}')],
            [InlineKeyboardButton(text='1 месяц PREMIUM', callback_data=f'donate_1month_{message.from_user.id}')],
            [InlineKeyboardButton(text='🧧 Удвоители', callback_data=f'activate_ticket_{message.from_user.id}')]
        ])
        await message.answer('Покупка 👑 PREMIUM 👑\n\n'
                             '🌟 Бонусы:\n'
                             '+50% к доходу\n'
                             'Возможность использовать любые символы в никнейме\n'
                             'Максимальная допустимая длина никнейма увеличена в 2 раза\n\n'
                             'Цена:\n1 день - 20 руб.\n1 неделя - 100 руб. (Выгоднее на 30%!).\n1 месяц - 300 руб. (Выгоднее на 50%!)\n\n'
                             f'❗ Кнопки оплаты предназначены только для пользователя {user[0]} ❗', reply_markup=markup)


@commands_router.message(Command('chats'))
async def cmd_chats(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_messages')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='📤 Отправить сообщение', callback_data=f'new_message_{message.from_user.id}')],
            [InlineKeyboardButton(text='📬 Чаты', callback_data=f'chats_num_1_{message.from_user.id}')]
        ])
        await message.answer(f'📫 Сообщения\n\nОбщайся с другими пользователями не выходя из бота.\n\nЧат со временем будет становиться лучше и удобнее для общения в рамках бота, советуем уже сейчас общаться здесь, чтобы привыкнуть и сразу осваивать новые функции', reply_markup=markup)
        

@commands_router.message(Command('top'))
async def cmd_top(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_top')
        bal = await conn.fetch('SELECT name, bal, userid FROM stats WHERE userid <> $1 ORDER BY bal DESC LIMIT 5', ADMIN[0])
        income = await conn.fetch('SELECT name, income, userid FROM stats WHERE userid <> $1 ORDER BY income DESC LIMIT 5', ADMIN[0])
        if message.from_user.id != ADMIN[0]:
            me_bal = await conn.fetchrow('WITH users_ranking AS (SELECT userid, name, bal, ROW_NUMBER() OVER (ORDER BY bal DESC) AS rank FROM stats WHERE userid <> $2) SELECT rank, bal, name, userid FROM users_ranking WHERE userid = $1', message.from_user.id, ADMIN[0])
            me_inc = await conn.fetchrow('WITH users_ranking AS (SELECT userid, name, income, ROW_NUMBER() OVER (ORDER BY income DESC) AS rank FROM stats WHERE userid <> $2) SELECT rank, income, name, userid FROM users_ranking WHERE userid = $1', message.from_user.id, ADMIN[0])
        text = ''
        num = 1
        text += '💵 Топ 5 игроков по балансу:'
        success = 0
        for user in bal:
            text += f'\n{num}) {user[0]} - {user[1]}$'
            num += 1
            if message.from_user.id != ADMIN[0] and user[2] == me_bal[3]:
                success = 1
        if success == 0 and message.from_user.id != ADMIN[0]:
            text += f'\n{me_bal[0]}) {me_bal[2]} - {me_bal[1]}'
        num = 1
        text += '\n\n💸 Топ 5 игроков по доходу:'
        success = 0
        for user in income:
            text += f'\n{num}) {user[0]} - {user[1]}$ / 10 мин.'
            num += 1
            if message.from_user.id != ADMIN[0] and user[2] == me_inc[3]:
                success = 1
        if success == 0 and message.from_user.id != ADMIN[0]:
            text += f'\n{me_inc[0]}) {me_inc[2]} - {me_inc[1]}'
        await message.answer(text)


@commands_router.message(Command('top_franchise'))
async def cmd_top_franchise(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_top_franchise')
        bal = await conn.fetch('SELECT name, income FROM networks WHERE owner_id != $1 ORDER BY income DESC LIMIT 10', ADMIN[0])
        text = ''
        num = 1
        text += '💸 Топ 10 франшиз по доходу за неделю:'
        for user in bal:
            text += f'\n{num}) {user[0]} - {user[1]}$'
            num += 1
        text += '\n\n❗ Топ 5 и 2 случайных игрока из топ 5 франшиз получат PREMIUM после сброса доходов франшиз, в понедельник, в 00:00 по МСК ❗'
        await message.answer(text)


@commands_router.message(Command('promo'))
async def cmd_promo(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, income FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_promo')
        if message.text[6:] != '':
            promo = await conn.fetchrow('SELECT * FROM promos WHERE name = $1', message.text[7:])
            if promo != None:
                if not message.from_user.id in promo[3]:
                    if promo[1] < promo[2]:
                        reward = ''
                        if promo[4] == 'money':
                            reward = f'{promo[5]}$'
                            await message.answer(f'Вы успешно активировали промокод! Вы получили: {reward}')
                            await conn.execute('UPDATE stats SET bal = bal + $1 WHERE userid = $2', promo[5], message.from_user.id)
                        elif promo[4] == 'income':
                            await message.answer(f'✅ Вы успешно активировали промокод! Вы получили: {promo[5]*user[1]*6}$')
                            await conn.execute('UPDATE stats SET bal = bal + $1 WHERE userid = $2', promo[5]*user[1]*6, message.from_user.id)
                        await conn.execute('UPDATE promos SET use = $1, users = array_append(users, $2) WHERE name = $3', promo[1]+1, message.from_user.id, promo[0])
                    else:
                        await message.answer('❌ Этот промокод уже кончился')
                else:
                    await message.answer('❌ Вы уже использовали этот промокод')
            else:
                await message.answer('⚠️ Такой промокод не найден')
        else:
            await message.answer('⚠️ Команду надо использовать в формате:\n /promo (проиокод)')


@commands_router.message(Command('profile'))
async def cmd_profile(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, taxes, bonus, tickets FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_profile')
        stats = await conn.fetchrow('SELECT name, pc, room, bal, income, network, premium, title FROM stats WHERE userid = $1', message.from_user.id)
        bufs = await conn.fetchrow('SELECT upgrade_Internet, upgrade_devices, upgrade_interior, upgrade_minibar, upgrade_service FROM stats WHERE userid = $1', message.from_user.id)
        network = await conn.fetchrow('SELECT name FROM networks WHERE owner_id = $1', stats[5])
        user_ad = await conn.fetchrow('SELECT * FROM ads WHERE userid = $1 ORDER BY dt DESC LIMIT 1', message.from_user.id)
        text = ''
        income = Decimal(str(stats[4]))
        prem = 0
        if stats[6] > datetime.datetime.today():
            date_time = str(stats[6])
            text += f'👑 PREMIUM 👑 до {date_time[8:10]}.{date_time[5:7]}.{date_time[0:4]} {date_time[11:16]}\n'
            prem = income/2
        
        summ = 0
        ad_inc = 0

        for buf in bufs:
            summ += income/100*buf
        
        for ad in ads:
            if user_ad != None and user_ad[1] == ad[0] and user_ad[3] + datetime.timedelta(hours=ad[4]+ad[5]) > datetime.datetime.today():
                ad_inc = income/100*user_ad[2]

        income = income + prem + summ +ad_inc
        
        if stats[7] != None:
            text += f'{stats[7]}\n'
        text += f'Профиль игрока <a href="tg://user?id={message.from_user.id}">{stats[0]}</a>:\n'
        text += f'\n🖥 Компьютеры: {stats[1]}/{stats[2]*5}\n⏫ Уровень комнаты: {stats[2]}\n'
        text += f'\n💵 Баланс: {stats[3]}$\n💸 Доход: {income}$ / 10 мин.\n💰 Чистый доход: {stats[4]}$ / 10 мин.\n'
        if user[3] > 0:
            text += f'\n🧧 У вас есть билеты удвоения: {user[3]}. Чтобы использовать его перейдите в /donate\n'
        if user[1] > taxes[stats[2]-1][1] / 3 * 2:
            text += f'\n⚠️ Высокая налоговая задолженность: {user[1]}$\nОплатить налоги: /pay_taxes\n'
        if network != None:
            text += f'\n🌐 Состоит в франшизе: {network[0]}\n'
        else:
            text += '\n🌐 Пользователь не состоит в франшизе\n'
        text += '\nИзменить никнейм: /nickname\nСтатистика игрока: /stats\nРефералы: /ref'
        if user[2] == 1:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🎁 Ежедневный бонус', callback_data=f'bonus_{message.from_user.id}')]
            ])
            await message.answer(text, reply_markup=markup, parse_mode='HTML')
        else:
            await message.answer(text, parse_mode='HTML')


@commands_router.message(Command('set_title'))
async def cmd_set_title(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_set_title')
        text = message.text.split(' ')
        if len(text) == 2:
            title = await conn.fetchrow('SELECT * FROM titles WHERE id = $1', text[1])
            if title != None:
                if message.from_user.id in title[1]:
                    await message.answer('🎖️ Вы успешно установили титул')
                    await conn.execute('UPDATE stats SET title = $1 WHERE userid = $2', title[0], message.from_user.id)
                else:
                    await message.answer('⚠️ Этот титул вам не доступен')
            else:
                await message.answer('❌ Такой титул не найден')
        else:
            await message.answer('⚠️ Команду нужно вводить в формате: /set_title (id титула*)')


@commands_router.message(Command('titles'))
async def cmd_titles(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_titles')
        titles = await conn.fetch('SELECT * FROM titles WHERE $1 = ANY(users)', message.from_user.id)
        text = '🎖️ Это ваши титулы:'
        for title in titles:
            text += f'\n{title[0]} ID: {title[2]}'
        text += '\nЧтобы установить титул введите:\n/set_title (id титула*)'
        await message.answer(text)


@commands_router.message(Command('cancel'))
async def cmd_cancel(message: Message, state: FSMContext):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_cancel')
        await state.clear()
        await message.answer('❌ Действие отменено')