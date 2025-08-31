
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from funcs import get_db_pool, update_data, add_action
from aiogram import Bot, Router, F
from conf import TOKEN


bot = Bot(token=TOKEN)

cmd_franchise_router = Router()


@cmd_franchise_router.message(F.text == '🌐 Франшизы')
async def msg_franchise(message: Message):
    await cmd_franchise(message)


@cmd_franchise_router.message(Command('allow_user'))
async def cmd_allow_user(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_allow_user')
        admins = await conn.fetchval('SELECT admins FROM networks WHERE owner_id = $1', user[1])
        requests = await conn.fetchval('SELECT requests FROM networks WHERE owner_id = $1', user[1])
        if user[1] != None:
            if int(message.text[12:]) in requests:
                if message.from_user.id in admins or message.from_user.id == user[1]:
                    net_user = await conn.fetchval('SELECT network FROM stats WHERE userid = $1', int(message.text[12:]))
                    if net_user == None:
                        await message.answer('✅ Вы успешно приняли заявку')
                        await bot.send_message(message.text[12:], '🎊 Вы приняты в франшизу')
                        await conn.execute('UPDATE stats SET network = $1 WHERE userid = $2', message.from_user.id, int(message.text[12:]))
                        await conn.execute('UPDATE networks SET requests = array_remove(requests, $1) WHERE owner_id = $2', int(message.text[12:]), message.from_user.id)
                    else:
                        await message.answer('❌ Пользователь уже состоит в другой франшизе')
                else:
                    await message.answer('❌ Вы не являетесь владельцем франшизы или её администратором')
            else:
                await message.answer('⚠️ Этот пользователь не отправлял заявку в вашу франшизу')
        else:
            await message.answer('❌ Вы не состоите в франшизе')


@cmd_franchise_router.message(Command('set_admin'))
async def cmd_set_admin(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_set_admin')
        if int(message.text[11:]) == message.from_user.id:
            await message.answer('⚠️ Нельзя назначить себя администратором')
        else:
            user = await conn.fetchval('SELECT userid FROM stats WHERE userid = $1 AND network = $2', int(message.text[11:]), message.from_user.id)
            if user != None:
                await message.answer('✅ Вы успешно назначили клуб администратором')
                await conn.execute('UPDATE networks SET admins = array_append(admins, $1) WHERE owner_id = $2', int(message.text[11:]), message.from_user.id)
            else:
                await message.answer('❌ Вы не являетесь владельцем франшизы или этот пользователь не найден в ней')


@cmd_franchise_router.message(Command('delete_admin'))
async def cmd_delete_admin(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_delete_admin')
        if int(message.text[13:]) == message.from_user.id:
            await message.answer('⚠️ Нельзя снять себя с должности администратора')
        else:
            user = await conn.fetchval('SELECT userid FROM stats WHERE userid = $1 AND network = $2', int(message.text[13:]), message.from_user.id)
            if user != None:
                await message.answer('✅ Вы успешно сняли клуб с должности администратора')
                await conn.execute('UPDATE networks SET admins = array_remove(admins, $1) WHERE owner_id = $2', int(message.text[13:]), message.from_user.id)
            else:
                await message.answer('❌ Вы не являетесь владельцем франшизы или этот пользователь не найден в ней')


@cmd_franchise_router.message(Command('delete_user'))
async def cmd_delete_user(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_delete_user')
        if int(message.text[13:]) == message.from_user.id:
            await message.answer('⚠️ Нельзя удалить себя')
        else:
            admins = await conn.fetchval('SELECT admins FROM networks WHERE owner_id = $1', user[1])
            user = await conn.fetchval('SELECT userid FROM stats WHERE userid = $1 AND network = $2', int(message.text[13:]), user[1])
            if int(message.text[13:]) == user[1]:
                await message.answer('❌ Нельзя удалить владельца')
            elif message.from_user.id in admins and int(message.text[13:]) in admins:
                await message.answer('❌ Нельзя удалить администратора')
            elif user != None:
                if message.from_user.id == user[1] or message.from_user.id in admins:
                    await message.answer('✅ Вы успешно исключили клуб из франшизы')
                    await bot.send_message(message.text[13:], '🫷 Ваш клуб был исключен из франшизы')
                    await conn.execute('UPDATE stats SET network = $1 WHERE userid = $2', None, int(message.text[13:]))
                    if int(message.text[13:]) in admins:
                        await conn.execute('UPDATE networks SET admins = array_remove(admins, $1) WHERE owner_id = $2', int(message.text[13:]), user[1])
                else:
                    await message.answer('❌ Вы не являетесь владельцем франшизы или её администратором')
            else:
                await message.answer('❌ Этот пользователь не найден в франшизе')


@cmd_franchise_router.message(Command('ban_user'))
async def cmd_ban_user(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_ban_user')
        if int(message.text[9:]) == message.from_user.id:
            await message.answer('⚠️ Нельзя забанить себя')
        else:
            admins = await conn.fetchval('SELECT admins FROM networks WHERE owner_id = $1', user[1])
            user = await conn.fetchval('SELECT userid FROM stats WHERE userid = $1 AND network = $2', int(message.text[9:]), user[1])
            if int(message.text[9:]) == user[1]:
                await message.answer('❌ Нельзя забанить владельца')
            elif message.from_user.id in admins and int(message.text[9:]) in admins:
                await message.answer('❌ Нельзя забанить администратора')
            elif user != None:
                if message.from_user.id == user[1] or message.from_user.id in admins:
                    await message.answer('✅ Вы успешно заблокировали доступ к франшизе этому клубу')
                    await conn.execute('UPDATE stats SET network = $1 WHERE userid = $2', None, int(message.text[9:]))
                    await conn.execute('UPDATE networks SET ban_users = array_append(ban_users, $1) WHERE owner_id = $2', int(message.text[9:]), user[1])
                    if int(message.text[13:]) in admins:
                        await conn.execute('UPDATE networks SET admins = array_remove(admins, $1) WHERE owner_id = $2', int(message.text[13:]), user[1])
                else:
                    await message.answer('❌ Вы не являетесь владельцем франшизы или её администратором')
            else:
                await message.answer('❌ Этот пользователь не находится в франшизе')


@cmd_franchise_router.message(Command('reban_user'))
async def cmd_reban_user(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_reban_user')
        if int(message.text[11:]) == message.from_user.id:
            await message.answer('⚠️ Нельзя разбанить себя')
        else:
            admins = await conn.fetchval('SELECT admins FROM networks WHERE owner_id = $1', user[1])
            user = await conn.fetchval('SELECT userid FROM stats WHERE userid = $1', int(message.text[11:]))
            if int(message.text[11:]) == user[1]:
                await message.answer('❌ Нельзя разбанить владельца')
            if message.from_user.id in admins and int(message.text[13:]) in admins:
                await message.answer('❌ Нельзя разбанить администратора')
            if user != None:
                if message.from_user.id == user[1] or message.from_user.id in admins:
                    await message.answer('✅ Вы успешно разблокировали доступ к франшизе этому клубу')
                    await conn.execute('UPDATE networks SET ban_users = array_remove(ban_users, $1) WHERE owner_id = $2', user, user[1])
                else:
                    await message.answer('❌ Вы не являетесь владельцем франшизы или её администратором')
            else:
                await message.answer('❌ Этот пользователь не найден')


@cmd_franchise_router.message(Command('franchise'))
async def cmd_franchise(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_franchise')
        if user[1] is None:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='🆕 Создать новую франшизу', callback_data=f'network_create_{message.from_user.id}')],
                [InlineKeyboardButton(text='🤝 Вступить в франшизу', callback_data=f'network_search_{message.from_user.id}')]
            ])
            await message.answer('🌐 Вы не состоите в франшизе', reply_markup=markup)
        else:
            network = await conn.fetchrow('SELECT name, owner_id, description, income, type, admins FROM networks WHERE owner_id = $1', user[1])
            if network[4] == 'request':
                markup1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='✏️ Изменить франшизу', callback_data=f'network_edit_{message.from_user.id}')],
                    [InlineKeyboardButton(text='👥 Участники', callback_data=f'network_members_1_{message.from_user.id}')],
                    [InlineKeyboardButton(text='📫 Заявки', callback_data=f'network_requests_{message.from_user.id}')],
                    [InlineKeyboardButton(text='📤 Сделать рассылку', callback_data=f'network_mailing_{message.from_user.id}')]
                ])
            else:
                markup1 = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='✏️ Изменить франшизу', callback_data=f'network_edit_{message.from_user.id}')],
                    [InlineKeyboardButton(text='👥 Участники', callback_data=f'network_members_1_{message.from_user.id}')],
                    [InlineKeyboardButton(text='📤 Сделать рассылку', callback_data=f'network_mailing_{message.from_user.id}')]
                ])
            if network[1] == message.from_user.id:
                markup1.inline_keyboard.extend([[InlineKeyboardButton(text='🔄️ Передать права на франшизу', callback_data=f'network_owner_{message.from_user.id}')],
                                               [InlineKeyboardButton(text='🗑️ Удалить франшизу', callback_data=f'network_delete_{message.from_user.id}')]])
            else:
                markup1.inline_keyboard.append([InlineKeyboardButton(text='Покинуть франшизу', callback_data=f'network_left_{message.from_user.id}')])
            net_type = ''
            if network[4] == 'open':
                net_type = 'Открытая'
            elif network[4] == 'close':
                net_type = 'Закрытая'
            elif network[4] == 'request':
                net_type = 'По заявке'
            markup2 = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Покинуть франшизу', callback_data=f'network_left_{message.from_user.id}')]
            ])
            members = await conn.fetchval('SELECT COUNT(*) FROM stats WHERE network = $1', network[1])
            admins = await conn.fetchval('SELECT admins FROM networks WHERE owner_id = $1', network[1])
            if network[1] == message.from_user.id or message.from_user.id in admins:
                await message.answer(f'🌐 Франшиза {network[0]}\n\n🆔 ID: {network[1]}\n💭 Описание: {network[2]}\n🔘 Статус: {net_type}\n\n👥 Количество клубов-участников: {members}\n\n💰 Заработано за эту неделю: {network[3]}$\n🏆 Топ франшизы: /franchise_info', reply_markup=markup1)
            else:
                await message.answer(f'🌐 Франшиза {network[0]}\n\n🆔 ID: {network[1]}\n💭 Описание: {network[2]}\n🔘 Статус: {net_type}\n\n👥 Количество клубов-участников: {members}\n\n💰 Заработано за эту неделю: {network[3]}$\n🏆 Топ франшизы: /franchise_info', reply_markup=markup2)


@cmd_franchise_router.message(Command('franchise_info'))
async def cmd_franchise_info(message: Message):
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow('SELECT name, network FROM stats WHERE userid = $1', message.from_user.id)
        if user is None:
            await message.answer('Сначала зарегистрируйтесь - /start')
            return
        await update_data(message.from_user.username, message.from_user.id)
        await add_action(message.from_user.id, 'cmd_franchise_info')
        info = await conn.fetch('SELECT name, net_inc FROM stats WHERE network = $1 ORDER BY net_inc DESC LIMIT 10', user[1])
        text = '💸 Топ 10 игроков твоей франшизы по заработанным $ за неделю:'
        num = 1
        for user in info:
            text += f'\n{num}) {user[0]} - {user[1]}$'
            num += 1
        await message.answer(text)
