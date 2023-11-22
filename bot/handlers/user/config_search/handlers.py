from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import SendMessage

from bot.handlers.user.handlers import config_search_page, main_page, cur_filtres
from bot.states import ConfSearchState
from aiogram.methods import DeleteMessage, EditMessageText
from bot.misc import bot, logger
from bot.markups.inline_markups import BrandInlineBuilder
from bot.utils import cfsch_messages
from bot.markups import inline_markups
from bot.utils import save_filters
from bot.controllers import user
from bot import text

cfsch_router = Router()

# DATA = {}

# MESSAGE MANAGERS
async def update_message(message_id: int, chat_id: int | str, state: FSMContext, error:bool = False):
    cur_state = await state.get_state()
    if cur_state is None:
        await config_search_page(state=state, chat_id=chat_id, msg=None)
        await DeleteMessage(message_id=message_id,
                            chat_id=chat_id).as_(bot=bot)
        return
    cur_state_name = cur_state.split(':')[-1]
    if error:
        text=cfsch_messages[cur_state_name]['text_error']
    else:
        text=cfsch_messages[cur_state_name]['text']
    try:
        reply_markup = await inline_markups.state_inline_markups(state)
        await EditMessageText(text=text, reply_markup=reply_markup, chat_id=chat_id, message_id=message_id).as_(bot=bot)
    except TelegramBadRequest:
        logger.exception('Edit Message Text Telegram Bad Request')

async def next(state: FSMContext, callback: CallbackQuery | None = None, chat_id: int | str | None = None):
    assert(callback is not None or chat_id is not None)
    cur_state = await state.get_state()
    await state.set_state(state=ConfSearchState.next(cur_state))
    if callback is not None:
        await callback.answer()
        await update_message(message_id=callback.message.message_id, chat_id=callback.message.chat.id, state=state, error=False)
    else:
        await update_message(message_id=(await state.get_data())['message_id'], chat_id=chat_id, state=state, error=False)

async def prev(state: FSMContext, callback: CallbackQuery):
    cur_state = await state.get_state()
    await state.set_state(state=ConfSearchState.pref(cur_state))
    cur_state = await state.get_state()
    await callback.answer()
    if cur_state == 'ConfSearchState:brand':
        await update_message_brand(callback=callback, state=state)
        return
    await update_message(message_id=callback.message.message_id, chat_id=callback.message.chat.id, state=state, error=False)

async def cfsch_on_error_tap(callback: CallbackQuery,  state: FSMContext) -> bool:
    cur_state = await state.get_state()
    user_data = await state.get_data()
    if cur_state is None or not user_data or callback.message.message_id != user_data['message_id']:
        await callback.answer('Ожидание ввода для этого сообщения закончилось', show_alert=True)
        await callback.message.delete()
        return True
    return False

@cfsch_router.message(ConfSearchState.brand)
@cfsch_router.message(ConfSearchState.region)
@cfsch_router.message(ConfSearchState.odds)
@cfsch_router.message(ConfSearchState.count_owners)
async def message_remover(msg: Message,  state: FSMContext):
    await msg.delete()

# HANDLE CALLBACKS
## main and back
@cfsch_router.callback_query(F.data == 'cfsch_main_page')
async def cfsch_main_page(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.clear()
    await main_page(msg=callback.message, state=state)
    await callback.answer()
    await callback.message.delete()

@cfsch_router.callback_query(F.data == 'cfsch_back')
async def cfsch_back(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await prev(callback=callback, state=state)

## cost
@cfsch_router.callback_query(F.data == 'cfsch_cost_all')
async def cfsch_cost_all(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(cost = 'all')
    await next(callback=callback, state=state)
    

@cfsch_router.message(ConfSearchState.cost)
async def cfsch_cost_message(msg: Message, state: FSMContext):
    validate_data = cfsch_messages['cost']['validator'](msg.text)
    state_data = await state.get_data()
    if validate_data is None:
        await update_message(message_id=state_data['message_id'], chat_id=msg.chat.id, state=state, error=True)
    else:
        await state.update_data(cost = validate_data)
        await next(chat_id=msg.chat.id, state=state)
    await msg.delete()

## region
@cfsch_router.callback_query(F.data == 'cfsch_region_moskva')
async def cfsch_region_moskva(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(region = 'moskva')
    await next(callback=callback, state=state)

@cfsch_router.callback_query(F.data == 'cfsch_region_spb')
async def cfsch_region_spb(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(region = 'sankt-peterburg')
    await next(callback=callback, state=state)

@cfsch_router.callback_query(F.data == 'cfsch_region_all')
async def cfsch_region_all(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(region = 'all')
    await next(callback=callback, state=state)

## mileage
@cfsch_router.callback_query(F.data == 'cfsch_mileage_all')
async def cfsch_mileage_all(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(mileage = 'all')
    await next(callback=callback, state=state)

@cfsch_router.message(ConfSearchState.mileage)
async def cfsch_mileage_message(msg: Message, state: FSMContext):
    validate_data = cfsch_messages['mileage']['validator'](msg.text)
    state_data = await state.get_data()
    if validate_data is None:
        await update_message(message_id=state_data['message_id'], chat_id=msg.chat.id, state=state, error=True)
    else:
        await state.update_data(mileage = validate_data)
        await next(chat_id=msg.chat.id, state=state)
    await msg.delete()

## year_release
@cfsch_router.callback_query(F.data == 'cfsch_year_release_all')
async def cfsch_year_release_all(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(year_release = 'all')
    await next(callback=callback, state=state)

@cfsch_router.message(ConfSearchState.year_release)
async def cfsch_year_release_message(msg: Message, state: FSMContext):
    validate_data = cfsch_messages['year_release']['validator'](msg.text)
    state_data = await state.get_data()
    if validate_data is None:
        await update_message(message_id=state_data['message_id'], chat_id=msg.chat.id, state=state, error=True)
    else:
        await state.update_data(year_release = validate_data)
        await next(chat_id=msg.chat.id, state=state)
    await msg.delete()

## count_owners
@cfsch_router.callback_query(F.data == 'cfsch_count_owners_all')
async def cfsch_count_owners_all(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(count_owners = 'all')
    await next(callback=callback, state=state)

@cfsch_router.callback_query(F.data == 'cfsch_count_owners_1')
async def cfsch_count_owners_1(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(count_owners = '1')
    await next(callback=callback, state=state)

@cfsch_router.callback_query(F.data == 'cfsch_count_owners_2')
async def cfsch_count_owners_2(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(count_owners = '2')
    await next(callback=callback, state=state)

@cfsch_router.callback_query(F.data == 'cfsch_count_owners_3')
async def cfsch_count_owners_3(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(count_owners = '3')
    await next(callback=callback, state=state)

@cfsch_router.callback_query(F.data == 'cfsch_count_owners_4')
async def cfsch_count_owners_4(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(count_owners = '4')
    await next(callback=callback, state=state)

# @cfsch_router.message(ConfSearchState.count_owners)
# async def cfsch_count_owners_message(msg: Message, state: FSMContext):
#     validate_data = cfsch_messages['count_owners']['validator'](msg.text)
#     state_data = await state.get_data()
#     if validate_data is None:
#         await update_message(message_id=state_data['message_id'], chat_id=msg.chat.id, state=state, error=True)
#     else:
#         await state.update_data(count_owners = validate_data)
#         await next(chat_id=msg.chat.id, state=state)
#     await msg.delete()

## odds
@cfsch_router.callback_query(F.data == 'cfsch_odds_all')
async def cfsch_odds_all(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(odds = 'all')
    await exit(from_user=callback.from_user, chat_id=callback.message.chat.id, state=state)

@cfsch_router.callback_query(F.data == 'cfsch_odds_low')
async def cfsch_odds_low(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    await state.update_data(odds = 'low')
    await next(callback=callback, state=state)

## odds_rate
@cfsch_router.message(ConfSearchState.odds_rate)
async def cfsch_odds_lower(msg: Message, state: FSMContext):
    validate_data = cfsch_messages['odds_rate']['validator'](msg.text)
    cur_data = await state.get_data()
    if validate_data is None:
        await update_message(message_id=cur_data['message_id'], chat_id=msg.chat.id, state=state, error=True)
    else:
        await state.update_data(odds_rate = validate_data)
        await exit(from_user=msg.from_user, chat_id=msg.chat.id, state=state)
    await msg.delete()

# exit
async def exit(from_user, chat_id, state:FSMContext):
    cur_data = await state.get_data()
    cur_user = await user.get_user(from_user=from_user, chat_id=chat_id)
    if not await save_filters(user=cur_user, data=cur_data.copy()):
        await SendMessage(chat_id=chat_id, text=text.error_filters).as_(bot=bot)
    await state.clear()
    await update_message(message_id=cur_data['message_id'], chat_id=chat_id, state=state)
    await cur_filtres(msg=None, chat_id=chat_id, state=state, from_user=from_user)

## brand
brand_router = Router()
cfsch_router.include_router(brand_router)

handler_list = [f'cfsch_brand_{h}' for h in BrandInlineBuilder.helps]

async def update_message_brand(callback: CallbackQuery,  state: FSMContext):
    cur_data = await state.get_data()
    await callback.answer()
    try:
        await callback.message.edit_reply_markup(reply_markup=BrandInlineBuilder(cur_data).get_keyboard())
    except TelegramBadRequest:
        logger.exception('Edit reply markup Telegram Bad Request')

def brand_wrapper(callback_data:str):
    async def wrap_corutine(callback: CallbackQuery, state: FSMContext, cb_data:str = callback_data):
        if await cfsch_on_error_tap(callback, state):
            return
        
        cur_data = await state.get_data()
        if cur_data.get('brand') is None:
                cur_data['brand'] = {}
        cb_data = cb_data.replace("cfsch_brand_", "")
        if cb_data == 'all':
            if len(cur_data['brand']) < len(handler_list) - 1:
                tmp_handler = [h.replace("cfsch_brand_", "") for h in handler_list]
                cur_data['brand'] = {h:h for h in tmp_handler if h != 'all'}
            else:
                cur_data['brand'] = {}
        else:
            if cur_data['brand'].get(cb_data) is None:
                cur_data['brand'][cb_data] = cb_data
            else:
                cur_data['brand'].pop(cb_data)

        await state.update_data(data=cur_data)
        await update_message_brand(callback=callback, state=state)
        
        
    return wrap_corutine

for handler in handler_list:
    brand_router.callback_query.register(brand_wrapper(handler), F.data == handler)

@brand_router.callback_query(F.data == 'cfsch_brand_approve')
async def cfsch_brand_approve(callback: CallbackQuery,  state: FSMContext):
    if await cfsch_on_error_tap(callback, state):
        return
    cur_data = await state.get_data()
    if cur_data.get('brand') is None or len(cur_data['brand']) == 0:
        await callback.answer('Вы не выбрали ни одной марки')
    else:
        await next(callback=callback, state=state)
