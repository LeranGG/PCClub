
import datetime
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Router, F, Bot
from yoomoney import Client
from conf import PAYMENT_TOKEN, TOKEN
from funcs import get_db_pool, update_data, add_action
from fsm import Mailing


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
        user = await conn.fetchrow('SELECT userid, name FROM stats WHERE userid = $1', callback.from_user.id)
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
            await callback.message.answer(f'📬 Выберите чат:\n\n[{user[0]}](tg://user?id={user[0]})', reply_markup=markup, parse_mode='markdown')
        else:
            await callback.message.answer('📬 У вас пока нет активных чатов')


@callback_router.callback_query(F.data.startswith('chat'))
async def cb_chat(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, name FROM stats WHERE userid = $1', callback.from_user.id)
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
        await callback.message.answer(f'{user[1]}: {messages[num-1][1]}\n\nДата отправки: {messages[num-1][2].strftime('%H:%M:%S %d.%m.%Y')}', reply_markup=markup)


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
            stats = await conn.fetchrow('SELECT premium, ref FROM stats WHERE userid = $1', callback.from_user.id)
            days = await conn.fetchval('SELECT days FROM orders WHERE label = $1', labels)
            if not callback.from_user.id in title:
                await conn.execute('UPDATE titles SET users = array_append(users, $1) WHERE id = $2', callback.from_user.id, 'first_donate')
            if stats[0] > datetime.datetime.today():
                await conn.execute('UPDATE stats SET premium = premium + $1 WHERE userid = $2', datetime.timedelta(days=days), callback.from_user.id)
            else:
                await conn.execute('UPDATE stats SET premium = NOW() + $1 WHERE userid = $2', datetime.timedelta(days=days), callback.from_user.id)
            await conn.execute('UPDATE orders SET success = 1 WHERE label = $1', labels)
            if stats[1] != None:
                prem = await conn.fetchval('SELECT premium FROM stats WHERE userid = $1', stats[1])
                if prem > datetime.datetime.today():
                    await conn.execute('UPDATE stats SET premium = premium + $1 WHERE userid = $2', datetime.timedelta(days=days/4), stats[1])
                else:
                    await conn.execute('UPDATE stats SET premium = NOW() + $1 WHERE userid = $2', datetime.timedelta(days=days/4), stats[1])
            await callback.message.edit_text('✅ Оплата прошла успешно. Премиум зачислен на твой аккаунт!')
        else:
            await callback.message.edit_text('❌ Не оплачено')