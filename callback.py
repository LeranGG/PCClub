
import datetime, uuid
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot
from yoomoney import Client, Quickpay
from conf import PAYMENT_TOKEN, TOKEN
from funcs import get_db_pool, update_data, add_action
from fsm import Mailing, Games


bot = Bot(token=TOKEN)

client = Client(PAYMENT_TOKEN)

callback_router = Router()


@callback_router.callback_query(F.data.startswith('new_message'))
async def cb_new_message(callback: CallbackQuery, state: FSMContext):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_new_message')
        await callback.message.answer('👤 Введите ID пользователя, которому адресовано сообщение')
        await state.set_state(Mailing.user)


@callback_router.callback_query(F.data.startswith('chats_num'))
async def cb_chats_num(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_chats_num')
        num = int(callback.data.split('_')[2])
        chats = await conn.fetch('SELECT chat_id, users FROM chats WHERE $1 = ANY(users) ORDER BY date_create', callback.from_user.id)
        if len(chats) > 0:
            if len(chats) == 1:
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f'{num}', callback_data=f'{num}')],
                    [InlineKeyboardButton(text='Открыть чат', callback_data=f'chat_{chats[num-1][0]}_1_{callback.from_user.id}')]
                ])
            elif num == 1:
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f'{num}', callback_data=f'{num}'),
                     InlineKeyboardButton(text=f'➡️', callback_data=f'chats_num_{num+1}_{callback.from_user.id}')],
                    [InlineKeyboardButton(text='Открыть чат', callback_data=f'chat_{chats[num-1][0]}_1_{callback.from_user.id}')]
                ])
            elif num == len(chats):
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f'⬅️', callback_data=f'chats_num_{num-1}_{callback.from_user.id}'),
                     InlineKeyboardButton(text=f'{num}', callback_data=f'{num}')],
                    [InlineKeyboardButton(text='Открыть чат', callback_data=f'chat_{chats[num-1][0]}_1_{callback.from_user.id}')]
                ])
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f'⬅️', callback_data=f'chats_num_{num-1}_{callback.from_user.id}'),
                     InlineKeyboardButton(text=f'{num}', callback_data=f'{num}'),
                     InlineKeyboardButton(text=f'➡️', callback_data=f'chats_num_{num+1}_{callback.from_user.id}')],
                    [InlineKeyboardButton(text='Открыть чат', callback_data=f'chat_{chats[num-1][0]}_1_{callback.from_user.id}')]
                ])
            user = chats[num-1][1]
            user.remove(callback.from_user.id)
            user = await conn.fetchrow('SELECT name, userid FROM stats WHERE userid = $1', user[0])
            await callback.message.answer(f'📬 Выберите чат:\n\n[{user[0]}](tg://user?id={user[1]})', reply_markup=markup, parse_mode='markdown')
        else:
            await callback.message.answer('📬 У вас пока нет активных чатов')


@callback_router.callback_query(F.data.startswith('chat'))
async def cb_chat(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_chat')
        num = int(callback.data.split('_')[2])
        messages = await conn.fetch('SELECT user_from, msg_text, msg_date FROM messages WHERE chat_id = $1 ORDER BY msg_date DESC', int(callback.data.split('_')[1]))
        if len(messages) == 1:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f'{num}', callback_data=f'{num}')]
            ])
        elif num == 1:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f'{num}', callback_data=f'{num}'),
                 InlineKeyboardButton(text=f'➡️', callback_data=f'chat_{callback.data.split('_')[1]}_{num+1}_{callback.from_user.id}')]
            ])
        elif num == len(messages):
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f'⬅️', callback_data=f'chat_{callback.data.split('_')[1]}_{num-1}_{callback.from_user.id}'),
                 InlineKeyboardButton(text=f'{num}', callback_data=f'{num}')]
            ])
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f'⬅️', callback_data=f'chat_{callback.data.split('_')[1]}_{num-1}_{callback.from_user.id}'),
                 InlineKeyboardButton(text=f'{num}', callback_data=f'{num}'),
                 InlineKeyboardButton(text=f'➡️', callback_data=f'chat_{callback.data.split('_')[1]}_{num+1}_{callback.from_user.id}')]
            ])
        user = await conn.fetchrow('SELECT name, userid FROM stats WHERE userid = $1', messages[num-1][0])
        await callback.message.answer(f'{user[0]}: {messages[num-1][1]}\n\nДата отправки: {messages[num-1][2].strftime('%H:%M:%S %d.%m.%Y')}', reply_markup=markup)


@callback_router.callback_query(F.data.startswith('cancel'))
async def cb_cancel(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_cancel')
        await callback.message.edit_text('❌ Действие отменено')


@callback_router.callback_query(F.data.startswith('success'))
async def cb_success(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_success')
        labels = await conn.fetch('SELECT label FROM orders WHERE userid = $1 AND success = 0', callback.from_user.id)
        history = client.operation_history()
        success = 0
        for label in labels:
            for operation in history.operations:
                if operation.label == str(label[0]):
                    if operation.status == 'success':
                        success = 1
                        labels = operation.label
                        
        if success == 1:
            title = await conn.fetchval('SELECT users FROM titles WHERE id = $1', 'first_donate')
            stats = await conn.fetchrow('SELECT premium, ref, active_ticket FROM stats WHERE userid = $1', callback.from_user.id)
            days = await conn.fetchval('SELECT days FROM orders WHERE label = $1', labels)
            if stats[2] == True:
                days += days
                await conn.execute('UPDATE stats SET active_ticket = False WHERE userid = $1', callback.from_user.id)
            if not callback.from_user.id in title:
                await conn.execute('UPDATE titles SET users = array_append(users, $1) WHERE id = $2', callback.from_user.id, 'first_donate')
            if stats[0] > datetime.datetime.today():
                await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', stats[0] + datetime.timedelta(days=days), callback.from_user.id)
            else:
                await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', datetime.datetime.today() + datetime.timedelta(days=days), callback.from_user.id)
            await conn.execute('UPDATE orders SET success = 1 WHERE label = $1', labels)
            if stats[1] != None:
                prem = await conn.fetchval('SELECT premium FROM stats WHERE userid = $1', stats[1])
                if prem > datetime.datetime.today():
                    await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', prem + datetime.timedelta(days=days/4), stats[1])
                else:
                    await conn.execute('UPDATE stats SET premium = $1 WHERE userid = $2', datetime.datetime.today() + datetime.timedelta(days=days/4), stats[1])
            await callback.message.edit_text('✅ Оплата прошла успешно. Премиум зачислен на твой аккаунт!')
        else:
            await callback.message.edit_text('❌ Не оплачено')


@callback_router.callback_query(F.data.startswith('activate_ticket_success'))
async def cb_activate_ticket_success(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_activate_ticket_success')
        tickets = await conn.fetchval('SELECT tickets FROM stats WHERE userid = $1', callback.from_user.id)
        if tickets != 0:
            await callback.message.edit_text('✅ Вы успешно активировали билет удвоения')
            await conn.execute('UPDATE stats SET active_ticket = True, tickets = tickets - 1 WHERE userid = $1', callback.from_user.id)
        else:
            await callback.message.edit_text('⚠️ У вас нету билетов удвоения')


@callback_router.callback_query(F.data.startswith('activate_ticket'))
async def cb_activate_ticket(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_activate_ticket')
        tickets = await conn.fetchval('SELECT tickets FROM stats WHERE userid = $1', callback.from_user.id)
        if tickets != 0:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='✅ Активировать', callback_data=f'activate_ticket_success_{callback.from_user.id}')],
                [InlineKeyboardButton(text='❌ Отмена', callback_data=f'cancel_{callback.from_user.id}')]
            ])
            await callback.message.edit_text(f'ℹ️ Билеты удваивают любой купленный вами донат.\n\nВы уверены что хотите активировать билет? У вас есть {tickets} билетов\n\n‼️ Активированные билеты не суммируются',
                                             reply_markup=markup)
        else:
            await callback.message.edit_text('⚠️ У вас нету билетов удвоения')


@callback_router.callback_query(F.data.startswith('donate_1day'))
async def cb_donate_1day(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_donate_1day')
        url = await generate_payment_link(20, uuid.uuid4(), 'Оплата PREMIUM 1 день', callback.from_user.id, 1)
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='💳 Оплатить', url=url)],
            [InlineKeyboardButton(text='✅ Проверить', callback_data=f'success_{callback.from_user.id}')]
        ])
        await callback.message.edit_text('Оплата 👑 PREMIUM 👑\n\nЦена: 20 руб.\nСрок: 1 день\n\n'
                             'Оплатите PREMIUM по кнопке ниже, и нажмите "Проверить"', reply_markup=markup)


@callback_router.callback_query(F.data.startswith('donate_1week'))
async def cb_donate_1week(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_donate_1week')
        url = await generate_payment_link(100, uuid.uuid4(), 'Оплата PREMIUM 1 неделя', callback.from_user.id, 7)
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='💳 Оплатить', url=url)],
            [InlineKeyboardButton(text='✅ Проверить', callback_data=f'success_{callback.from_user.id}')]
        ])
        await callback.message.edit_text('Оплата 👑 PREMIUM 👑\n\nЦена: 100 руб.\nСрок: 1 неделя\n\n'
                             'Оплатите PREMIUM по кнопке ниже, и нажмите "Проверить"', reply_markup=markup)


@callback_router.callback_query(F.data.startswith('donate_1month'))
async def cb_donate_1month(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_donate_1month')
        url = await generate_payment_link(300, uuid.uuid4(), 'Оплата PREMIUM 1 месяц', callback.from_user.id, 30)
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='💳 Оплатить', url=url)],
            [InlineKeyboardButton(text='✅ Проверить', callback_data=f'success_{callback.from_user.id}')]
        ])
        await callback.message.edit_text('Оплата 👑 PREMIUM 👑\n\nЦена: 300 руб.\nСрок: 1 месяц\n\n'
                             'Оплатите PREMIUM по кнопке ниже, и нажмите "Проверить"', reply_markup=markup)


async def generate_payment_link(amount, label, description, userid, days):
    quickpay = Quickpay(
        receiver='4100118865752483',
        quickpay_form='shop',
        paymentType='AC',
        sum=amount,
        label=label,
        targets=description,
        successURL='https://t.me/PCClub_sBOT'
    )
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute('INSERT INTO orders (userid, label, product, success, amount, days) VALUES ($1, $2, $3, 0, $4, $5)',
                           userid, label, description, amount, days)
    return quickpay.redirected_url


@callback_router.callback_query(F.data.startswith('game_1'))
async def cb_game_1(callback: CallbackQuery, state: FSMContext):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_game_1')
        await callback.message.edit_text('❓ На что вы хотите сделать ставку?\nВведите орел/решка или /cancel для отмены действия')
        await state.set_state(Games.game1_bet)


@callback_router.callback_query(F.data.startswith('game_2'))
async def cb_game_2(callback: CallbackQuery, state: FSMContext):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_game_2')
        await callback.message.edit_text('❓ На что вы хотите сделать ставку?\nВведите число от 1 до 6 или /cancel для отмены действия')
        await state.set_state(Games.game2_bet)