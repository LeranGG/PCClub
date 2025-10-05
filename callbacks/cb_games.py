
from aiogram import Router, F
from fsm import Games
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from funcs.funcs import get_db_pool, update_data, add_action


cb_games_router = Router()


@cb_games_router.callback_query(F.data.startswith('game_1'))
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


@cb_games_router.callback_query(F.data.startswith('game_2'))
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