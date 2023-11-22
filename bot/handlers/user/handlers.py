from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.methods import SendMessage
from aiogram.types import User as TgUser

import bot.text as text
from bot import utils
from bot.states import ConfSearchState
from bot.markups import inline_markups, reply_markups
from bot.controllers import user
from bot.utils import cfsch_messages, save_filters, is_can_subscribe
from bot.misc import bot


router = Router()

# COMMANDS
@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await state.clear()
    cur_user = await user.get_user(from_user=msg.from_user, chat_id=msg.chat.id)
    await msg.answer(text.start, reply_markup=reply_markups.main_markup(cur_user.notifi_status))

@router.message(Command("help"))
async def helper(msg: Message):
    await msg.answer(text.help_text)

# MAIN PAGE
@router.message(F.text == '🌀 Главная')
@router.message(F.text == 'Главная')
async def main_page(msg: Message, state: FSMContext):
    await state.clear()
    cur_user = await user.get_user(from_user=msg.from_user, chat_id=msg.chat.id)
    await msg.answer(text.main_page, reply_markup=reply_markups.main_markup(cur_user.notifi_status))

# LK
@router.message(F.text == 'Личный кабинет')
async def lk_page(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer(text.lk, reply_markup=reply_markups.lk_markup())

@router.message(F.text == 'Поддержка')
async def support(msg: Message, state: FSMContext):
    await msg.answer(text.support)

@router.message(F.text == 'Информация о тарифе')
async def tarif_info(msg: Message, state: FSMContext):
    cur_user = await user.get_user(from_user=msg.from_user, chat_id=msg.chat.id)
    await msg.answer(text.get_info_tarif(cur_user.demo_status, cur_user.full_time_end, cur_user.demo_counter), reply_markup=inline_markups.lk_choose_tarif())

@router.message(F.text == 'Туториал')
async def tutorial(msg: Message, state: FSMContext):
    await msg.answer(text.tutorial)

@router.callback_query(F.data == 'lk_1week')
async def lk_1week_callback(callback: CallbackQuery):
    await callback.message.answer(text.get_info_pay(period='1w'))
    await callback.answer()

@router.callback_query(F.data == 'lk_1mounth')
async def lk_1mounth_callback(callback: CallbackQuery):
    await callback.message.answer(text.get_info_pay(period='1m'))
    await callback.answer()
    
@router.callback_query(F.data == 'lk_3mounth')
async def lk_3mounth_callback(callback: CallbackQuery):
    await callback.message.answer(text.get_info_pay(period='3m'))
    await callback.answer()

# CONFIG SEARCH
@router.message(F.text == 'Настройка поиска')
async def config_search_page(msg: Message | None, state: FSMContext, chat_id: int | str | None = None):
    assert(msg is not None or chat_id is not None)
    await state.clear()
    if chat_id is None:
        chat_id = msg.chat.id
    await SendMessage(chat_id=chat_id, text=text.config_search_main, reply_markup=reply_markups.config_search_markup()).as_(bot=bot)

@router.message(F.text == 'Текущие фильтры')
async def cur_filtres(msg: Message | None, state: FSMContext, from_user:TgUser | None = None, chat_id: int | str | None = None):
    assert(msg is not None or chat_id is not None and from_user is not None)
    if chat_id is None:
        chat_id = msg.chat.id
        from_user = msg.from_user
    cur_user = await user.get_user(from_user=from_user, chat_id=chat_id)
    filtres_text = text.get_filtres(cur_user)
    await SendMessage(chat_id=chat_id, reply_markup=reply_markups.config_search_markup(), **filtres_text.as_kwargs()).as_(bot=bot)

@router.message(F.text == 'Настроить фильтры')
async def config_filters(msg: Message, state: FSMContext):
    await utils.delete_reply_markups(msg=msg)
    await state.clear()
    await state.set_state(state=ConfSearchState.start())
    cur_state = await state.get_state()
    assert(cur_state is not None)
    cur_state = cur_state.split(':')[-1]
    cfsch_message = await msg.answer(text=cfsch_messages[cur_state]['text'], reply_markup=await inline_markups.state_inline_markups(state))
    await state.update_data(message_id = cfsch_message.message_id)

@router.message(F.text == 'Получать все обьявления')
async def config_filters(msg: Message, state: FSMContext):
    await msg.answer(text=text.all_filters, reply_markup=inline_markups.all_filters())

@router.callback_query(F.data == 'all_filters_agree')
async def all_filters_agree_callback(callback: CallbackQuery, state: FSMContext):
    cur_user = await user.get_user(callback.from_user, chat_id=callback.message.chat.id)
    if not await save_filters(user=cur_user):
        await callback.answer(text.error_filters)
        await callback.message.delete()
    else:
        await cur_filtres(msg=None, from_user=callback.from_user, chat_id=callback.message.chat.id, state=state)
        await callback.answer()
        await callback.message.delete()

@router.callback_query(F.data == 'all_filters_cancel')
async def all_filters_cancel_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.delete()

# SUBSCRIBE AND UNSUBSCRIBE
@router.message(F.text == 'Подписаться на уведомления')
async def lk_page(msg: Message, state: FSMContext):
    cur_user = await user.get_user(from_user=msg.from_user, chat_id=msg.chat.id)
    not_subscribe_reason = is_can_subscribe(cur_user)
    if not_subscribe_reason is None:
        cur_user.notifi_status = True
        await cur_user.save(update_fields=['notifi_status'])
        await msg.answer(text=text.subscribe)
        await main_page(msg=msg, state=state)
    else:
        answer = f'Вы не можете подписаться на уведомления\nПричина: {not_subscribe_reason}'
        await msg.answer(text=answer)
    
@router.message(F.text == 'Приостановить отправку уведомлений')
async def lk_page(msg: Message, state: FSMContext):
    cur_user = await user.get_user(from_user=msg.from_user, chat_id=msg.chat.id)
    cur_user.notifi_status = False
    await cur_user.save(update_fields=['notifi_status'])
    await msg.answer(text=text.unsubscribe)
    await main_page(msg=msg, state=state)
