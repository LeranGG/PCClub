
import uuid
from aiogram import Router, F
from yoomoney import Quickpay
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from funcs import get_db_pool, update_data, add_action


cb_donate_router = Router()


@cb_donate_router.callback_query(F.data.startswith('donate_1day'))
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


@cb_donate_router.callback_query(F.data.startswith('donate_1week'))
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


@cb_donate_router.callback_query(F.data.startswith('donate_1month'))
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
