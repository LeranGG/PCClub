
import datetime
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Router, F
from funcs import get_db_pool, update_data, add_action
from aiogram.fsm.context import FSMContext
from fsm import Network_edit, Network_mailing, Network_search, Reowner
from math import ceil


cb_network_router = Router()


@cb_network_router.callback_query(F.data.startswith('network_members'))
async def cb_network_members(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_members')
        members = await conn.fetch('SELECT name, userid, net_inc FROM stats WHERE network = $1 ORDER BY net_inc DESC', user[1])
        num = int(callback.data.split('_')[-2])
        text = '👥 Все клубы-участники франшизы'
        number = 1
        admins = await conn.fetchval('SELECT admins FROM networks WHERE owner_id = $1', user[1])
        for user in members[5*(num-1):5*(num)]:
            text += f'\n{number}. <a href="tg://user?id={user[1]}">{user[0]}</a> ID: {user[1]} Доход: {user[2]}$'
            if user[1] in admins:
                text += ' (админ.)'
            elif user[1] == user[1]:
                text += ' (владелец)'
            number += 1
            if len(members) < 4:
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f'{num}', callback_data=f'{num}')],
                    [InlineKeyboardButton(text='🔙 Назад', callback_data=f'network_{callback.from_user.id}')]
                ])
            elif num == 1:
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f'{num}', callback_data=f'{num}'),
                     InlineKeyboardButton(text=f'➡️', callback_data=f'network_members_{num+1}_{callback.from_user.id}')],
                    [InlineKeyboardButton(text='🔙 Назад', callback_data=f'network_{callback.from_user.id}')]
                ])
            elif num >= ceil(len(members)/5):
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f'⬅️', callback_data=f'network_members_{num-1}_{callback.from_user.id}'),
                     InlineKeyboardButton(text=f'{num}', callback_data=f'{num}')],
                    [InlineKeyboardButton(text='🔙 Назад', callback_data=f'network_{callback.from_user.id}')]
                ])
            else:
                markup = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f'⬅️', callback_data=f'network_members_{num-1}_{callback.from_user.id}'),
                     InlineKeyboardButton(text=f'{num}', callback_data=f'{num}'),
                     InlineKeyboardButton(text=f'➡️', callback_data=f'network_members_{num+1}_{callback.from_user.id}')],
                    [InlineKeyboardButton(text='🔙 Назад', callback_data=f'network_{callback.from_user.id}')]
                ])
        text += '\n\nℹ️ Доступные команды:'
        text += '\nИсключить игрока - /delete_user'
        text += '\nЗабанить игрока /ban_user'
        text += '\nРазбанить игрока /reban_user'
        if callback.from_user.id == user[1]:
            text += '\nВыдать админку /set_admin'
            text += '\nСнять админку /delete_admin'
        text += '\n‼️ Команды надо вводить в формате:\n/(команда) (id игрока)'
        await callback.message.edit_text(text, parse_mode='HTML', reply_markup=markup)


@cb_network_router.callback_query(F.data.startswith('network_requests'))
async def cb_network_requests(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_requests')
        requests = await conn.fetchval('SELECT requests FROM networks WHERE owner_id = $1', callback.from_user.id)
        text = '📫 Все заявки на вход:'
        num = 1
        for user in requests:
            text += f'\n{num}. <a href="tg://user?id={user}">{user}</a>'
            num += 1
        text += '\n✅ Принять: /allow_user (id игрока*)'
        await callback.message.edit_text(text, parse_mode='HTML')


@cb_network_router.callback_query(F.data.startswith('network_edit_name'))
async def cb_network_edit_name(callback: CallbackQuery, state: FSMContext):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_edit_name')
        await callback.message.edit_text('📝 Введите новое название для франшизы\nВведите /cancel для отмены действия')
        await state.set_state(Network_edit.name)


@cb_network_router.callback_query(F.data.startswith('network_edit_description'))
async def cb_network_edit_description(callback: CallbackQuery, state: FSMContext):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_edit_description')
        await callback.message.edit_text('📝 Введите новое описание для франшизы\nВведите /cancel для отмены действия')
        await state.set_state(Network_edit.desc)


@cb_network_router.callback_query(F.data.startswith('network_type'))
async def cb_network_type(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_type')
        net_type = callback.data.split('_')[-2]
        if net_type == 'open':
            net_type2 = 'Открытая'
        elif net_type == 'close':
            net_type2 = 'Закрытая'
        elif net_type == 'request':
            net_type2 = 'По заявке'
        await conn.execute('UPDATE networks SET type = $1 WHERE owner_id = $2', net_type, user[1])
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔙 Назад', callback_data=f'network_{callback.from_user.id}')]
        ])
        await callback.message.edit_text(f'✅ Вы успешно изменили статус франшизы на "{net_type2}"', reply_markup=markup)


@cb_network_router.callback_query(F.data.startswith('network_edit_type'))
async def cb_network_edit_type(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_edit_type')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔓 Открытая', callback_data=f'network_type_open_{callback.from_user.id}')],
            [InlineKeyboardButton(text='🔒 Закрытая', callback_data=f'network_type_close_{callback.from_user.id}')],
            [InlineKeyboardButton(text='✉️ По заявке', callback_data=f'network_type_request_{callback.from_user.id}')]
        ])
        await callback.message.edit_text('❓ Какой статус франшизы вы хотите установить?', reply_markup=markup)


@cb_network_router.callback_query(F.data.startswith('network_mailing'))
async def cb_network_mailing(callback: CallbackQuery, state: FSMContext):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_mailing')
        network = await conn.fetchrow('SELECT admins, mailing FROM networks WHERE owner_id = $1', userid[1])
        if callback.from_user.id in network[0] or callback.from_user.id == userid[1]:
            if network[1] + datetime.timedelta(hours=1) <= datetime.datetime.today():
                await callback.message.edit_text('✉️ Введите текст для рассылки или /cancel для отмены действия')
                await state.set_state(Network_mailing.text)
            else:
                await callback.message.edit_text('⚠️ Рассылку можно отправлять только раз в час')
        else:
            await callback.message.edit_text('❌ Вы не являетесь владельцем франшизы')


@cb_network_router.callback_query(F.data.startswith('network_edit'))
async def cb_network_edit(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_edit')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🪧 Название', callback_data=f'network_edit_name_{callback.from_user.id}')],
            [InlineKeyboardButton(text='💬 Описание', callback_data=f'network_edit_description_{callback.from_user.id}')],
            [InlineKeyboardButton(text='🔘 Статус', callback_data=f'network_edit_type_{callback.from_user.id}')],
            [InlineKeyboardButton(text='🔙 Назад', callback_data=f'network_{callback.from_user.id}')]
        ])
        await callback.message.edit_text('❓ Что будем изменять?', reply_markup=markup)


@cb_network_router.callback_query(F.data.startswith('network_delete_success'))
async def cb_network_delete_success(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_delete_success')
        await conn.execute('DELETE FROM networks WHERE owner_id = $1', callback.from_user.id)
        users = await conn.fetch('SELECT userid FROM stats WHERE network = $1', callback.from_user.id)
        if len(users) > 1:
            for user in users:
                await conn.execute('UPDATE stats SET network = $1, net_inc = $2 WHERE userid = $3', None, 0, user[0])
        else:
            await conn.execute('UPDATE stats SET network = $1, net_inc = $2 WHERE userid = $3', None, 0, callback.from_user.id)
        await callback.message.edit_text('✅ Франшиза удалена!')


@cb_network_router.callback_query(F.data.startswith('network_delete'))
async def cb_network_delete(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_delete')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Да.', callback_data=f'network_delete_success_{callback.from_user.id}')],
            [InlineKeyboardButton(text='❌ НЕТ!', callback_data=f'cancel_{callback.from_user.id}')]
        ])
        await callback.message.edit_text('‼️ Подтвердите удаление', reply_markup=markup)


@cb_network_router.callback_query(F.data.startswith('network_left_success'))
async def cb_network_left_success(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, net_inc, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_left_success')
        income = await conn.fetchval('SELECT income FROM networks WHERE owner_id = $1', user[2])
        await conn.execute('UPDATE stats SET network = NULL, net_inc = 0 WHERE userid = $2', callback.from_user.id)
        await conn.execute('UPDATE networks SET income = $1 WHERE owner_id = $2', income-user[1], callback.from_user.id)
        await callback.message.edit_text('↩️ Вы покинули франшизу!')


@cb_network_router.callback_query(F.data.startswith('network_left'))
async def cb_network_left(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_left')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='✅ Да.', callback_data=f'network_left_success_{callback.from_user.id}')],
            [InlineKeyboardButton(text='❌ НЕТ!', callback_data=f'cancel_{callback.from_user.id}')]
        ])
        await callback.message.edit_text('‼️ Подтвердите выход', reply_markup=markup)


@cb_network_router.callback_query(F.data.startswith('network_create'))
async def cb_network_create(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_create')
        if user[1] is None:
            await conn.execute('INSERT INTO networks (owner_id) VALUES ($1)', callback.from_user.id)
            await conn.execute('UPDATE stats SET network = $1 WHERE userid = $2', callback.from_user.id, callback.from_user.id)
            await callback.message.edit_text('✅ Вы успешно создали франшизу')
        else:
            await callback.message.edit_text('🫸 Вы уже состоите в франшизе')


@cb_network_router.callback_query(F.data.startswith('network_search_id'))
async def cb_network_search_id(callback: CallbackQuery, state: FSMContext):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_search_id')
        if user[1] is None:
            await callback.message.edit_text('🆔 Введите ID или точное название франшизы в которую хотите вступить\nВведите /cancel для отмены действия')
            await state.set_state(Network_search.id)
        else:
            await callback.message.edit_text('🫸 Вы уже состоите в франшизе')
    
    
@cb_network_router.callback_query(F.data.startswith('network_search_num_'))
async def cb_network_search_num(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_search_num')
        if user[1] is None:
            franchises = await conn.fetch('SELECT owner_id, name, description, income FROM networks WHERE type != $1 ORDER BY income DESC', 'close')
            if len(franchises) != 0:
                num = int(callback.data.split('_')[-2])
                text = f'Франшиза {franchises[num-1][1]}\n\n'
                text += f'Описание: {franchises[num-1][2]}\n'
                text += f'Заработано за эту неделю: {franchises[num-1][3]}'
                if len(franchises) == 1:
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f'{num}', callback_data=f'{num}')],
                        [InlineKeyboardButton(text='Вступить', callback_data=f'network_join_{franchises[num-1][0]}_{callback.from_user.id}')]
                    ])
                elif num == 1:
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f'{num}', callback_data=f'{num}'),
                         InlineKeyboardButton(text=f'➡️', callback_data=f'network_search_num_{num+1}_{callback.from_user.id}')],
                        [InlineKeyboardButton(text='Вступить', callback_data=f'network_join_{franchises[num-1][0]}_{callback.from_user.id}')]
                    ])
                elif num == len(franchises):
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f'⬅️', callback_data=f'network_search_num_{num-1}_{callback.from_user.id}'),
                         InlineKeyboardButton(text=f'{num}', callback_data=f'{num}')],
                        [InlineKeyboardButton(text='Вступить', callback_data=f'network_join_{franchises[num-1][0]}_{callback.from_user.id}')]
                    ])
                else:
                    markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text=f'⬅️', callback_data=f'network_search_num_{num-1}_{callback.from_user.id}'),
                         InlineKeyboardButton(text=f'{num}', callback_data=f'{num}'),
                         InlineKeyboardButton(text=f'➡️', callback_data=f'network_search_num_{num+1}_{callback.from_user.id}')],
                        [InlineKeyboardButton(text='Вступить', callback_data=f'network_join_{franchises[num-1][0]}_{callback.from_user.id}')]
                    ])
                await callback.message.edit_text(text, reply_markup=markup)
            else:
                await callback.message.edit_text('⚠️ Франшиз пока нет, но вы можете создать первую')
        else:
            await callback.message.edit_text('🫸 Вы уже состоите в франшизе')


@cb_network_router.callback_query(F.data.startswith('network_owner'))
async def cb_network_owner(callback: CallbackQuery, state: FSMContext):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_owner')
        await callback.message.answer('🆔 Введите ID пользователя которого хотите назначить владельцем франшизы или /cancel для отмены действия')
        await state.set_state(Reowner.userid)


@cb_network_router.callback_query(F.data.startswith('network_search_'))
async def cb_network_search(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_search')
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f'📜 Доступные франшизы', callback_data=f'network_search_num_1_{callback.from_user.id}')],
            [InlineKeyboardButton(text=f'🔍 Поиск по ID или названию', callback_data=f'network_search_id_{callback.from_user.id}')],
        ])
        await callback.message.edit_text('❓ Выберите метод поиска франшизы:', reply_markup=markup)


@cb_network_router.callback_query(F.data.startswith('network_join'))
async def cb_network_join(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network_join')
        data = callback.data.split('_')
        if user[1] is None:
            info = await conn.fetchrow('SELECT type, requests, ban_users FROM networks WHERE owner_id = $1', int(data[2]))
            if not callback.from_user.id in info[2]:
                if info[0] == 'open':
                    await conn.execute('UPDATE stats SET network = $1 WHERE userid = $2', int(data[2]), callback.from_user.id)
                    await callback.message.edit_text('🤝 Вы успешно присоединились к франшизе!')
                elif info[0] == 'close':
                    await callback.message.edit_text('🔒 Эта франшиза является закрытой!')
                elif info[0] == 'request':
                    await conn.execute('UPDATE networks SET requests = array_append(requests, $1)', callback.from_user.id)
                    await callback.message.edit_text('📨 Вы успешно подали заявку на вступление!')
            else:
                await callback.message.edit_text('😔 Вы были исключены из этой франшизы, и по этому не можете в нее вступить')
        else:
            await callback.message.edit_text('🫸 Вы уже состоите в франшизе')


@cb_network_router.callback_query(F.data.startswith('network'))
async def cb_network(callback: CallbackQuery):
    pool = await get_db_pool()
    userid = callback.data.split('_')[-1]
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT userid, network FROM stats WHERE userid = $1', callback.from_user.id)
        if user == None or user[0] != int(userid):
            await callback.answer('⚠️ Это не твое сообщение', show_alert=True)
            return
        await update_data(callback.from_user.username, callback.from_user.id)
        await add_action(callback.from_user.id, 'cb_network')
        if user[1] is None:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🆕 Создать новую франшизу', callback_data=f'network_create_{callback.from_user.id}')],
                [InlineKeyboardButton(text='🤝 Вступить в франшизу', callback_data=f'network_search_{callback.from_user.id}')]
            ])
            await callback.message.edit_text('🌐 Вы не состоите в франшизе', reply_markup=markup)
        else:
            network = await conn.fetchrow('SELECT name, owner_id, description, income, type, admins FROM networks WHERE owner_id = $1', user[1])
            if network[4] == 'request':
                markup1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='✏️ Изменить франшизу', callback_data=f'network_edit_{callback.from_user.id}')],
                    [InlineKeyboardButton(text='👥 Участники', callback_data=f'network_members_1_{callback.from_user.id}')],
                    [InlineKeyboardButton(text='📫 Заявки', callback_data=f'network_requests_{callback.from_user.id}')],
                    [InlineKeyboardButton(text='📤 Сделать рассылку', callback_data=f'network_mailing_{callback.from_user.id}')]
                ])
            else:
                markup1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='✏️ Изменить франшизу', callback_data=f'network_edit_{callback.from_user.id}')],
                    [InlineKeyboardButton(text='👥 Участники', callback_data=f'network_members_1_{callback.from_user.id}')],
                    [InlineKeyboardButton(text='📤 Сделать рассылку', callback_data=f'network_mailing_{callback.from_user.id}')]
                ])
            if network[1] == callback.from_user.id:
                markup1.inline_keyboard.extend([[InlineKeyboardButton(text='🔄️ Передать права на франшизу', callback_data=f'network_owner_{callback.from_user.id}')],
                                                [InlineKeyboardButton(text='🗑️ Удалить франшизу', callback_data=f'network_delete_{callback.from_user.id}')]])
            else:
                markup1.inline_keyboard.append([InlineKeyboardButton(text='Покинуть франшизу', callback_data=f'network_left_{callback.from_user.id}')])
            net_type = ''
            if network[4] == 'open':
                net_type = 'Открытая'
            elif network[4] == 'close':
                net_type = 'Закрытая'
            elif network[4] == 'request':
                net_type = 'По заявке'
            markup2 = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Покинуть франшизу', callback_data=f'network_left_{callback.from_user.id}')]
            ])
            members = await conn.fetchval('SELECT COUNT(*) FROM stats WHERE network = $1', network[1])
            admins = await conn.fetchval('SELECT admins FROM networks WHERE owner_id = $1', network[1])
            if network[1] == callback.from_user.id or callback.from_user.id in admins:
                await callback.message.edit_text(f'🌐 Франшиза {network[0]}\n\n🆔 ID: {network[1]}\n💭 Описание: {network[2]}\n🔘 Статус: {net_type}\n\n👥 Количество клубов-участников: {members}\n\n💰 Заработано за эту неделю: {network[3]}$\n🏆 Топ франшизы: /franchise_info', reply_markup=markup1)
            else:
                await callback.message.edit_text(f'🌐 Франшиза {network[0]}\n\n🆔 ID: {network[1]}\n💭 Описание: {network[2]}\n🔘 Статус: {net_type}\n\n👥 Количество клубов-участников: {members}\n\n💰 Заработано за эту неделю: {network[3]}$\n🏆 Топ франшизы: /franchise_info', reply_markup=markup2)
