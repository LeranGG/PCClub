
from aiogram.filters import Command
from aiogram.types import Message
from conf import ADMIN, TOKEN
from funcs.funcs import get_db_pool
from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
import datetime, secrets, string
from aiogram.fsm.context import FSMContext
from fsm import Send_channel

bot = Bot(token=TOKEN)

cmd_admin_router = Router()


@cmd_admin_router.message(Command('send_users'))
async def cmd_send_users(message: Message):
    if message.from_user.id == ADMIN[0]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            users = await conn.fetch('SELECT userid FROM stats')
            num = 1
            for user in users:
                try:
                    await bot.send_message(user[0], message.text[12:])
                except TelegramForbiddenError as e:
                    if "user is deactivated" in str(e):
                        await conn.execute('DELETE FROM stats WHERE userid = $1', user[0])
                    elif "bot was blocked" in str(e):
                        print(f"{num}) Пользователь {user[0]} заблокировал бота")
                    else:
                        print(f"{num}) Неизвестная ForbiddenError: {e}")
                except TelegramBadRequest as e:
                    if "chat not found" in str(e).lower():
                        print(f"{num}) {user[0]} не писал боту")
                    else:
                        print(f"{num}) Другая BadRequest: {e}")
                except Exception as e:
                    print(f"{num}) Непредвиденная ошибка: {e}")


@cmd_admin_router.message(Command('active'))
async def cmd_active(message: Message):
    if message.from_user.id == ADMIN[0]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            text = message.text.split(' ', 1)
            active = await conn.fetch('SELECT userid FROM actions WHERE dt >= $1', datetime.datetime.now() - datetime.timedelta(days=int(text[1])))
            users = len({el['userid'] for el in active})
            await message.answer(f'Активные пользователи за последние {text[1]} дней: {users}')


@cmd_admin_router.message(Command('add_promo'))
async def cmd_add_promo(message: Message):
    if message.from_user.id == ADMIN[0]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            text = message.text.split(' ')
            alph = string.ascii_letters + string.digits
            promo = ''.join(secrets.choice(alph) for _ in range(10))
            await conn.execute('INSERT INTO promos (name, use_max, reward, quantity) VALUES ($1, $2, $3, $4)', promo, int(text[1]), text[2], int(text[3]))
            await message.answer(f'Промокод создан: `{promo}`', parse_mode='markdown')


@cmd_admin_router.message(Command('stat'))
async def cmd_stat(message: Message):
    if message.from_user.id == ADMIN[0]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            stats = await conn.fetchrow('SELECT * FROM stats WHERE userid = $1', int(message.text[6:]))
            text = f'Статистика пользователя:\nНик: {stats[9]}\nЮзернейм: {stats[8]}\nБаланс: {stats[1]}\nУр. комнаты: {stats[2]}\nКоличество компьютеров: {stats[3]}\nДоход: {stats[5]}\nЗарегистрирован: {stats[6]}\nСеть: {stats[7]}\nВесь доход: {stats[10]}\nПремиум до {stats[11]}\nРеферал: {stats[12]}'
            await bot.send_message(message.from_user.id, text)


@cmd_admin_router.message(Command('stat_network'))
async def cmd_stat_network(message: Message):
    if message.from_user.id == ADMIN[0]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            stats = await conn.fetchrow('SELECT * FROM networks WHERE owner_id = $1', int(message.text[14:]))
            text = f'Статистика франшизы:\nНазвание: {stats[0]}\nОписание: {stats[2]}\nЗаработок за неделю: {stats[3]}'
            await bot.send_message(message.from_user.id, text)


@cmd_admin_router.message(Command('bot_info'))
async def cmd_bot_info(message: Message):
    if message.from_user.id == ADMIN[0]:
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            stats = await conn.fetchval('SELECT COUNT(*) FROM stats')
            networks = await conn.fetchval('SELECT COUNT(*) FROM networks')
            active = await conn.fetch('SELECT userid FROM actions WHERE dt >= $1', datetime.datetime.now() - datetime.timedelta(days=3))
            not_bots = await conn.fetchval('SELECT COUNT(*) FROM stats WHERE bal != 1000')
            users = len({el['userid'] for el in active})
            await message.answer(f'Статистика бота:\nКоличество игроков: {stats}\nКоличество франшиз: {networks}\nАктивные пользователи: {users}\nНе боты: {not_bots}')


@cmd_admin_router.message(Command('set_bal'))
async def cmd_set_bal(message: Message):
    if message.from_user.id in ADMIN and TOKEN == '7391256097:AAGVbvFUMW5ShfffjsPFFvFl9QONZ2kJbu8':
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute('UPDATE stats SET bal = $1 WHERE userid = $2', int(message.text[9:]), message.from_user.id)


@cmd_admin_router.message(Command('set'))
async def cmd_set(message: Message):
    if message.from_user.id == ADMIN[0] or (message.from_user.id in ADMIN and TOKEN == '7391256097:AAGVbvFUMW5ShfffjsPFFvFl9QONZ2kJbu8'):
        text = message.text.split(' ')
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            try:
                await conn.execute(f'UPDATE stats SET {text[1]} = $1 WHERE userid = $2', int(text[2]), int(text[3]))
                await message.answer('Успешно')
            except Exception as e:
                await message.answer(str(e))


@cmd_admin_router.message(Command('delete'))
async def cmd_delete(message: Message):
    if message.from_user.id in ADMIN and TOKEN == '7391256097:AAGVbvFUMW5ShfffjsPFFvFl9QONZ2kJbu8':
        pool = await get_db_pool()
        async with pool.acquire() as conn:
            await conn.execute('DELETE FROM stats')
            await conn.execute('DELETE FROM pc')
            await conn.execute('DELETE FROM networks')
            await conn.execute('DELETE FROM orders')
            await conn.execute('DELETE FROM promos')
            await conn.execute('DELETE FROM titles')
            await conn.execute('DELETE FROM messages')
            await conn.execute('DELETE FROM chats')
            await conn.execute('DELETE FROM ads')
            await message.answer('Почистил')
            

@cmd_admin_router.message(Command('send_channel'))
async def cmd_send_channel(message: Message, state: FSMContext):
    if message.from_user.id == ADMIN[0]:
        await bot.send_message(message.from_user.id, 'Укажите URL\nВведите /cancel для отмены действия')
        await state.set_state(Send_channel.url)