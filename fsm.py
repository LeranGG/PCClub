
import re, datetime, asyncio
from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from funcs import get_db_pool, update_data, add_action
from random import randint
from decimal import Decimal, getcontext
from conf import TOKEN, PCCLUB
from aiogram.fsm.state import State, StatesGroup


bot = Bot(token=TOKEN)

getcontext().prec = 50

fsm_router = Router()


class Network_search(StatesGroup):
    id = State()

class Network_edit(StatesGroup):
    name = State()
    desc = State()

class Games(StatesGroup):
    game1_bet = State()
    game1_amount = State()
    game2_bet = State()
    game2_amount = State()

class Network_mailing(StatesGroup):
    text = State()

class Mailing(StatesGroup):
    user = State()
    text = State()

class Reowner(StatesGroup):
    userid = State()

class Send_channel(StatesGroup):
    url = State()
    text = State()
    
class Rename(StatesGroup):
    name = State()


@fsm_router.message(Network_search.id)
async def Network_id(message: Message, state: FSMContext):
    await state.clear()
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Network_id')
        if message.text.isdigit():
            network = await conn.fetchrow('SELECT * FROM networks WHERE owner_id = $1', int(message.text))
        else:
            network = await conn.fetchrow('SELECT * FROM networks WHERE name = $1', message.text)
        if network is None:
            await message.answer('❌ Ничего не найдено')
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='↪️ Вступить', callback_data=f'network_join_{network[1]}_{message.from_user.id}')]
            ])
            status = ''
            if network[5] == 'open':
                status = 'Открытая'
            elif network[5] == 'close':
                status = 'Закрытая'
            elif network[5] == 'request':
                status = 'По заявке'
            await message.answer(f'🌐 Франшиза найдена!\nНазвание: {network[0]}\nОписание: {network[2]}\nСтатус: {status}', reply_markup=markup)


@fsm_router.message(Reowner.userid)
async def Reowner_userid(message: Message, state: FSMContext):
    await state.clear()
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Reowner_userid')
        if message.text.isdigit():
            foundUser = await conn.fetchval('SELECT userid FROM stats WHERE network = $1 AND userid = $2', message.from_user.id, int(message.from_user.id))
            if foundUser:
                await message.answer('🔄️ Вы успешно передали все права на франшизу')
                await conn.execute('UPDATE networks SET admins = array_remove(admins, $1) WHERE owner_id = $2', int(message.text), message.from_user.id)
                await conn.execute('UPDATE networks SET owner_id = $1 WHERE owner_id = $2', int(message.text), message.from_user.id)
                await conn.execute('UPDATE stats SET network = $1 WHERE network = $2', int(message.text), message.from_user.id)
            else:
                await message.answer('❌ Такой пользователь не найден в вашей франшизе')
        else:
            await message.answer('⚠️ Введите корректный ID')


@fsm_router.message(Network_mailing.text)
async def Network_mailing_text(message: Message, state: FSMContext):
    await state.clear()
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Network_mailing_text')
        members = await conn.fetch('SELECT userid FROM stats WHERE network = $1 AND userid != $1', user[1])
        for member in members:
            try:
                await bot.send_message(member[0], f'📥 Вам пришла рассылка от владельца франшизы: {message.text}')
            except Exception:
                pass
        await conn.execute('UPDATE networks SET mailing = $1 WHERE owner_id = $2', datetime.datetime.today(), message.from_user.id)
        await message.answer('📥 Рассылка успешно отправлена всем участникам франшизы')


@fsm_router.message(Network_edit.name)
async def Network_name(message: Message, state: FSMContext):
    if len(message.text) <= 50:
        await state.clear()
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
            if user is None:
                await message.answer('Сначала зарегистрируйтесь - /start')
                return
            await update_data(message.from_user.username, message.from_user.id)
            await add_action(message.from_user.id, 'Network_name')
            if bool(re.fullmatch(r"[а-яА-Яa-zA-Z0-9 '\"]+", message.text)):
                name = await conn.fetchrow('SELECT * FROM networks WHERE name = $1', message.text)
                if name is None:
                    await conn.execute('UPDATE networks SET name = $1 WHERE owner_id = $2', message.text, user[1])
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='🔙 Назад', callback_data=f'network_{message.from_user.id}')]
                    ])
                    await message.answer('✅ Вы успешно изменили название франшизы', reply_markup=markup)
                else:
                    await message.answer('❌ Это название уже занято')
            else:
                await message.answer('⚠️ Можно использовать только русские и английские буквы, а так же цифры')
    else:
        await message.answer('❌ Название слишком длинное')


@fsm_router.message(Network_edit.desc)
async def Network_desc(message: Message, state: FSMContext):
    if len(message.text) <= 500:
        await state.clear()
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
            if user is None:
                await message.answer('Сначала зарегистрируйтесь - /start')
                return
            await update_data(message.from_user.username, message.from_user.id)
            await add_action(message.from_user.id, 'Network_desc')
            await conn.execute('UPDATE networks SET description = $1 WHERE owner_id = $2', message.text, user[1])
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🔙 Назад', callback_data=f'network_{message.from_user.id}')]
            ])
            await message.answer('✅ Вы успешно изменили описание франшизы', reply_markup=markup)
    else:
        await message.answer('❌ Описание слишком длинное')


@fsm_router.message(Games.game1_bet)
async def Game1_bet(message: Message, state: FSMContext):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Game1_bet')
        if message.text.lower() in ["орел", 'решка', 'орёл']:
            await state.update_data(bet=message.text.lower().replace('ё', 'е'))
            await state.set_state(Games.game1_amount)
            await message.answer('❓ Сколько вы хотите поставить денег?\nВведите целое число (минимум 5000) или /cancel для отмены действия')
        else:
            await message.answer('⚠️ Ставкой может быть только орел или решка')


@fsm_router.message(Games.game1_amount)
async def Game1_amount(message: Message, state: FSMContext):
    await state.clear()
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, bal FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Game1_amount')
        if message.text.isdigit():
            if int(message.text) >= 5000:
                if int(message.text) <= user[1]:
                    value = randint(1, 100)
                    if value <= 49:
                        await conn.execute('UPDATE stats SET bal = bal + $1 WHERE userid = $2', int(message.text), message.from_user.id)
                        await message.answer(f'🎊 Вы угадали и получаете {int(message.text)*2}$')
                    else:
                        await conn.execute('UPDATE stats SET bal = bal - $1 WHERE userid = $2', int(message.text), message.from_user.id)
                        await message.answer(f'💥 Вы не угадали и теряете {message.text}$')
                else:
                    await message.answer('❌ У вас не хватает $')
            else:
                await message.answer('❌ Минимальная ставка 5000$')
        else:
            await message.answer('⚠️ Можно использовать только целые числа')


@fsm_router.message(Games.game2_bet)
async def Game2_bet(message: Message, state: FSMContext):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Game2_bet')
        if message.text.isdigit() and int(message.text) in [1, 2, 3, 4, 5, 6]:
            await state.update_data(bet=int(message.text))
            await state.set_state(Games.game2_amount)
            await message.answer('❓ Сколько вы хотите поставить денег?\nВведите целое число (минимум 5000) или /cancel для отмены действия')
        else:
            await message.answer('⚠️ Ставкой может быть только число от 1 до 6')


@fsm_router.message(Games.game2_amount)
async def Game2_amount(message: Message, state: FSMContext):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, bal FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Game2_amount')
        if message.text.isdigit():
            if int(message.text) >= 5000:
                if int(message.text) <= user[1]:
                    sent_dice = await message.answer_dice(emoji='🎲')
                    await asyncio.sleep(3)
                    data = await state.get_data()
                    if sent_dice.dice.value == data.get('bet'):
                        await conn.execute('UPDATE stats SET bal = bal + $1 WHERE userid = $2', int(message.text)*5, message.from_user.id)
                        await message.answer(f'🎊 Вы угадали и получаете {int(message.text)*6}$')
                    else:
                        await conn.execute('UPDATE stats SET bal = bal - $1 WHERE userid = $2', int(message.text), message.from_user.id)
                        await message.answer(f'💥 Вы не угадали и теряете {message.text}$')
                else:
                    await message.answer('❌ У вас не хватает $')
            else:
                await message.answer('❌ Минимальная ставка 5000$')
        else:
            await message.answer('⚠️ Можно использовать только целые числа')
    await state.clear()


@fsm_router.message(Mailing.user)
async def Mailing_user(message: Message, state: FSMContext):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Mailing_user')
        if not message.text.isdigit():
            await message.answer('⚠️ В айди могут быть только цифры')
            return
        user = await conn.fetchval('SELECT userid FROM stats WHERE userid = $1', int(message.text))
        if user != None:
            await state.update_data(user=int(message.text))
            await message.answer('✍️ Теперь введите текст сообщения')
            await state.set_state(Mailing.text)
            return
        await message.answer('❌ Такой пользователь не найден')


@fsm_router.message(Mailing.text)
async def Mailing_text(message: Message, state: FSMContext):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Mailing_text')
        if len(message.text) > 500:
            await message.answer('❌ Текст не может быть больше 500 символов')
        else:
            data = await state.get_data()
            chat = await conn.fetchval('SELECT chat_id FROM chats WHERE users @> ARRAY[$1::bigint, $2::bigint]', message.from_user.id, data.get('user'))
            try:
                if chat == None:
                    chat = randint(1, 9223372036854775807)
                    await conn.execute('INSERT INTO chats (chat_id, users) VALUES ($1, $2)', chat, [message.from_user.id, data.get('user')])
                await conn.execute('INSERT INTO messages (msg_text, user_from, chat_id) VALUES ($1, $2, $3)', message.text, message.from_user.id, chat)
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='✉️ Открыть сообщение', callback_data=f'chat_{chat}_1_{data.get("user")}')]
                ])
                await bot.send_message(data.get('user'), '📫 Вы получили новое сообщение', reply_markup=markup)
                await message.answer('✉️ Сообщение успешно отправлено')
            except Exception:
                await message.answer('❌ Этому пользователю сейчас не получится отправить сообщение!')
        await state.clear()


@fsm_router.message(Send_channel.url)
async def Send_channel_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    await bot.send_message(message.from_user.id, 'Укажите текст\nВведите /cancel для отмены действия')
    await state.set_state(Send_channel.text)


@fsm_router.message(Send_channel.text)
async def Send_channel_text(message: Message, state: FSMContext):
    data = await state.get_data()
    data = data.get('url')
    text = message.text.replace('_', f'\\_')
    text = text.replace('Подробнее об обновлении', f'[Подробнее об обновлении]({data})')
    await bot.send_message(PCCLUB, text, disable_web_page_preview=True, parse_mode='markdown')
    await state.clear()


@fsm_router.message(Rename.name)
async def Rename_name(message: Message, state: FSMContext):
    await state.clear()
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, premium FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'Rename_name')
        if user[1] < datetime.datetime.today():
            if len(message.text) <= 15:
                if bool(re.fullmatch(r"[а-яА-Яa-zA-Z0-9 '\"]+", message.text)):
                    name = await conn.fetchrow('SELECT * FROM stats WHERE name = $1', message.text)
                    if name is None:
                        await conn.execute('UPDATE stats SET name = $1 WHERE userid = $2', message.text, message.from_user.id)
                        await message.answer('✅ Вы успешно изменили никнейм')
                    else: 
                        await message.answer('⚠️ Этот никнейм уже занят')
                else:
                    await message.answer('⚠️ Без PREMIUM можно использовать только русские и английские буквы, а так же цифры')
            else:
                await message.answer('❌ Никнейм слишком длинный, максимальная длинна никнейма 15 символов')
        else:
            if len(message.text) <= 30:
                name = await conn.fetchrow('SELECT * FROM stats WHERE name = $1', message.text)
                if name is None:
                    await conn.execute('UPDATE stats SET name = $1 WHERE userid = $2', message.text, message.from_user.id)
                    await message.answer('✅ Вы успешно изменили никнейм')
                else:
                    await message.answer('⚠️ Этот никнейм уже занят')
            else:
                await message.answer('❌ Никнейм слишком длинный, максимальная длинна никнейма 30 символов')
