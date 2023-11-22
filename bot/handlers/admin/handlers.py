from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters.state import State
from aiogram.methods import DeleteMessage, EditMessageText, SendMessage
from aiogram.exceptions import TelegramBadRequest


import bot.text as text
from bot.models import User
from  bot.markups import inline_markups, reply_markups
from bot.controllers import user
from bot.states import AdminState
from bot.utils import delete_reply_markups, admin_messages, validator_user_id
from bot.misc import bot, logger

from datetime import date, timedelta

router_admin = Router()

# MAIN
@router_admin.message(Command("admin"))
async def start_handler(msg: Message | None, state: FSMContext, chat_id: int | str | None = None, user_id = None):
    assert(msg is not None or chat_id is not None and user_id is not None)
    if chat_id is None:
            chat_id = msg.chat.id
            user_id = msg.from_user.id
    cur_user = await user.user_exists(user_id=user_id)
    if cur_user is not None and await cur_user.is_admin():
        await state.clear()
        await SendMessage(chat_id=chat_id, text=text.greet_admin, reply_markup=reply_markups.admin_main_murkups()).as_(bot=bot)

async def start_add_rm(msg: Message, state: FSMContext, new_state:State, msg_text:str):
    await delete_reply_markups(msg=msg)
    await state.clear()
    await state.set_state(state=new_state)
    cur_state = await state.get_state()
    assert(cur_state is not None)
    if cur_state == AdminState.admin_add_rm:
        await state.update_data(target = 'admin')
    if cur_state == AdminState.user_add_rm_permission:
        await state.update_data(target = 'user')
    cur_state = cur_state.split(':')[-1]
    message = await msg.answer(text=msg_text, reply_markup=await inline_markups.state_inline_markups(state))
    await state.update_data(message_id = message.message_id)

@router_admin.message(F.text == 'Добавить/Удалить админа')
async def stats(msg: Message, state: FSMContext):
    cur_user = await user.get_user(from_user=msg.from_user, chat_id=msg.chat.id)
    if await cur_user.is_admin():
        await start_add_rm(msg=msg, state=state, new_state=AdminState.admin_add_rm, msg_text=text.AdminText.add_rm_admin)

@router_admin.message(F.text == 'Добавить/Удалить пользователя')
async def add_rm_admin(msg: Message, state: FSMContext):
    cur_user = await user.get_user(from_user=msg.from_user, chat_id=msg.chat.id)
    if await cur_user.is_admin():
        await start_add_rm(msg=msg, state=state, new_state=AdminState.user_add_rm_permission, msg_text=text.AdminText.add_rm_user_permission)

@router_admin.message(F.text == 'Показать всех пользователей')
async def add_rm_admin(msg: Message, state: FSMContext):
    cur_user = await user.get_user(from_user=msg.from_user, chat_id=msg.chat.id)
    if await cur_user.is_admin():
        users = await User.all()
        for user_i in users:
            await msg.answer(text=str(user_i))

# ADD/RM ADMIN
async def update_message(message_id: int, chat_id: int | str, user_id:int, state: FSMContext, error:bool = False):
    cur_state = await state.get_state()
    if cur_state is None:
        await start_handler(state=state, chat_id=chat_id, user_id=user_id, msg=None)
        await DeleteMessage(message_id=message_id,
                            chat_id=chat_id).as_(bot=bot)
        return
    cur_state_name = cur_state.split(':')[-1]
    if error:
        text:str=admin_messages[cur_state_name]['text_error']
    else:
        text:str=admin_messages[cur_state_name]['text']

    if cur_state_name == 'admin_confirm':
        cur_data = await state.get_data()
        text = text.format(user_id=cur_data['user_id'])
    if cur_state_name == 'user_confirm':
        cur_data = await state.get_data()
        if cur_data['timeframe'] == '1w':
            timeframe='Одну Неделю'
        if cur_data['timeframe'] == '1m':
            timeframe='Один Месяц'
        if cur_data['timeframe'] == '3m':
            timeframe='Три Месяца'
        text = text.format(user_id=cur_data['user_id'], timeframe=timeframe)
    try:
        reply_markup = await inline_markups.state_inline_markups(state)
        await EditMessageText(text=text, reply_markup=reply_markup, chat_id=chat_id, message_id=message_id).as_(bot=bot)
    except TelegramBadRequest:
        logger.exception('Edit Message Text Telegram Bad Request')

@router_admin.message(AdminState.admin_add_rm)
@router_admin.message(AdminState.user_add_rm_permission)
@router_admin.message(AdminState.user_input_timeframe)
@router_admin.message(AdminState.user_confirm)
@router_admin.message(AdminState.admin_confirm)
async def message_remover(msg: Message,  state: FSMContext):
    await msg.delete()

async def admin_on_error_tap(callback: CallbackQuery,  state: FSMContext) -> bool:
    cur_state = await state.get_state()
    user_data = await state.get_data()
    if cur_state is None or not user_data or callback.message.message_id != user_data['message_id']:
        await callback.answer('Ожидание ввода для этого сообщения закончилось', show_alert=True)
        await callback.message.delete()
        return True
    return False

async def next(state: FSMContext, callback: CallbackQuery | None = None, chat_id: int | str | None = None, user_id: int | None = None):
    assert(callback is not None or chat_id is not None and user_id is not None)
    cur_state = await state.get_state()
    await state.set_state(state=AdminState.next(cur_state))
    if callback is not None:
        await callback.answer()
        await update_message(message_id=callback.message.message_id, chat_id=callback.message.chat.id, user_id=callback.from_user.id, state=state, error=False)
    else:
        await update_message(message_id=(await state.get_data())['message_id'], chat_id=chat_id, user_id=user_id, state=state, error=False)

# CANCEL AND BACK
@router_admin.callback_query(F.data == 'admin_cancel')
async def admin_cancel(callback: CallbackQuery,  state: FSMContext):
    if await admin_on_error_tap(callback, state):
        return
    await state.clear()
    await start_handler(chat_id=callback.message.chat.id, state=state, user_id=callback.from_user.id, msg=None)
    await callback.answer()
    await callback.message.delete()

@router_admin.callback_query(F.data == 'admin_back')
async def admin_back(callback: CallbackQuery,  state: FSMContext):
    if await admin_on_error_tap(callback, state):
        return
    cur_state = await state.get_state()
    await state.set_state(state=AdminState.pref(cur_state))
    await callback.answer()
    await update_message(message_id=callback.message.message_id, chat_id=callback.message.chat.id, user_id=callback.from_user.id, state=state, error=False)

# ADD/RM
@router_admin.callback_query(F.data == 'admin_add')
async def admin_add(callback: CallbackQuery,  state: FSMContext):
    if await admin_on_error_tap(callback, state):
        return
    await state.update_data(action = 'add')
    await next(callback=callback, state=state)

@router_admin.callback_query(F.data == 'admin_rm')
async def admin_rm(callback: CallbackQuery,  state: FSMContext):
    if await admin_on_error_tap(callback, state):
        return
    await state.update_data(action = 'rm')
    await next(callback=callback, state=state)

# INPUT ID
@router_admin.message(AdminState.user_input_id)
@router_admin.message(AdminState.admin_input_id)
async def cfsch_cost_message(msg: Message, state: FSMContext):
    validate_user_id = await validator_user_id(msg.text)
    state_data = await state.get_data()
    if validate_user_id is None:
        await update_message(message_id=state_data['message_id'], chat_id=msg.chat.id, user_id=msg.from_user.id, state=state, error=True)
    else:
        await state.update_data(user_id = validate_user_id)
        await next(chat_id=msg.chat.id, user_id=msg.from_user.id, state=state)
    await msg.delete()

# TIMEFRAME
@router_admin.callback_query(F.data == 'admin_timeframe_1w')
async def admin_timeframe_1w(callback: CallbackQuery,  state: FSMContext):
    if await admin_on_error_tap(callback, state):
        return
    await state.update_data(timeframe = '1w')
    await next(callback=callback, state=state)

@router_admin.callback_query(F.data == 'admin_timeframe_1m')
async def admin_timeframe_1m(callback: CallbackQuery,  state: FSMContext):
    if await admin_on_error_tap(callback, state):
        return
    await state.update_data(timeframe = '1m')
    await next(callback=callback, state=state)

@router_admin.callback_query(F.data == 'admin_timeframe_3m')
async def admin_timeframe_3m(callback: CallbackQuery,  state: FSMContext):
    if await admin_on_error_tap(callback, state):
        return
    await state.update_data(timeframe = '3m')
    await next(callback=callback, state=state)

# CONFIRM AND VALIDATE
@router_admin.callback_query(F.data == 'admin_confirm')
async def admin_confirm(callback: CallbackQuery,  state: FSMContext):
    if await admin_on_error_tap(callback, state):
        return
    cur_data = await state.get_data()
    target_user = await User.filter(user_id=cur_data['user_id']).first()
    if target_user is None:
        await callback.answer(text.error_add_rm)
        await next(callback=callback, state=state)
        return
    if cur_data['target'] == 'admin':
        if cur_data['action'] == 'add':
            target_user.admin_status = True
        if cur_data['action'] == 'rm':
            target_user.admin_status = False
    if cur_data['target'] == 'user':
        if cur_data['action'] == 'add':
            start_timeframe = date.today()
            if cur_data['timeframe'] == '1w':
                end_timeframe = date.today() + timedelta(days=7)
            if cur_data['timeframe'] == '1m':
                end_timeframe = date.today() + timedelta(days=30)
            if cur_data['timeframe'] == '3m':
                end_timeframe = date.today() + timedelta(days=90)
            target_user.demo_status = False
            target_user.full_time_start = start_timeframe
            target_user.full_time_end = end_timeframe
            target_user.notifi_status = False
        if cur_data['action'] == 'rm':
            target_user.demo_status = True
            target_user.demo_counter = 0
            target_user.full_time_start = None
            target_user.full_time_end = None
            target_user.notifi_status = False
    await target_user.save(update_fields=['admin_status', 'demo_status', 'demo_counter', 'full_time_start', 'full_time_end', 'notifi_status'])
    cur_state = (await state.get_state()).split(":")[-1]
    if cur_state == 'admin_confirm':
        message_popup = text.AdminText.success_admin
    if cur_state == 'user_confirm':
        message_popup = text.AdminText.success_user
    await callback.answer(text=message_popup)
    await next(callback=callback, state=state)