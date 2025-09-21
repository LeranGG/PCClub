
import asyncio
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from funcs import get_db_pool, update_data, add_action
from aiogram import Router, F
from random import randint
from decimal import getcontext


cmd_games_router = Router()

getcontext().prec = 50


@cmd_games_router.message(F.text == '🎮 Игры')
async def msg_casino(message: Message):
    await cmd_casino(message)


@cmd_games_router.message(Command('games'))
async def cmd_casino(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_casino')
        if message.chat.type == 'private':
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🪙 Монетка', callback_data=f'game_1_{message.from_user.id}')],
                [InlineKeyboardButton(text='🎲 Кубик', callback_data=f'game_2_{message.from_user.id}')]
            ])
            await message.answer('🎮 Какую игру вы хотите сыграть?', reply_markup=markup)
        else:
            await message.answer('🎮 Какую игру вы хотите сыграть?\n🪙 Монетка - !game1 (ставка) (сумма ставки)\n🎲 Кубик - !game2 (ставка) (сумма ставки)')


@cmd_games_router.message(Command('dice'))
async def cmd_casino_chat(message: Message):
    sent_dice = await message.answer_dice(emoji='🎲')
    await asyncio.sleep(4)
    dice_value = sent_dice.dice.value
    await message.answer(f'🎲 Результат: {dice_value}')


@cmd_games_router.message(F.text.startswith('!game1'))
async def cmd_game1_chat(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, bal FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_game1_chat')
        command = message.text[1:].split(' ')
        if len(command) == 3 and command[2].isdigit() and command[1].lower() in ['орел', 'решка', 'орёл']:
            if int(command[2]) >= 5000:
                if int(command[2]) <= user[1]:
                    value = randint(1, 100)
                    if value <= 49:
                        await conn.execute('UPDATE stats SET bal = bal + $1 WHERE userid = $2', int(command[2]), message.from_user.id)
                        await message.answer(f'🎊 Вы угадали и получаете {int(command[2])*2}$')
                    else:
                        await conn.execute('UPDATE stats SET bal = bal - $1 WHERE userid = $2', int(command[2]), message.from_user.id)
                        await message.answer(f'💥 Вы не угадали и теряете {command[2]}$')
                else:
                    await message.answer('❌ У вас не хватает $')
            else:
                await message.answer('❌ Минимальная ставка 5000')
        else:
            await message.answer('⚠️ Команду нужно использовать в формате:\n!game1 (орел/решка*) (целое число*)')


@cmd_games_router.message(F.text.startswith('!game2'))
async def cmd_game2_chat(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, bal FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_game2_chat')
        command = message.text[1:].split(' ')
        if command[1].isdigit() and int(command[1]) in [1, 2, 3, 4, 5, 6] and command[2].isdigit():
            if int(command[2]) >= 5000:
                if int(command[2]) <= user[1]:
                    sent_dice = await message.answer_dice(emoji='🎲')
                    await asyncio.sleep(3)
                    dice_value = sent_dice.dice.value
                    if dice_value == int(command[1]):
                        await conn.execute('UPDATE stats SET bal = bal + $1 WHERE userid = $2', int(command[2])*5, message.from_user.id)
                        await message.answer(f'🎊 Вы угадали и получаете {int(command[2])*6}$')
                    else:
                        await conn.execute('UPDATE stats SET bal = bal - $1 WHERE userid = $2', int(command[2]), message.from_user.id)
                        await message.answer(f'💥 Вы не угадали и теряете {command[2]}$')
                else:
                    await message.answer('❌ У вас не хватает $')
            else:
                await message.answer('❌ Минимальная ставка 5000')
        else:
            await message.answer('⚠️ Команду нужно использовать в формате:\n!game2 (число от 1 до 6*) (целое число*)')
