from aiogram.types import Message
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

import re
from typing import Any, Dict, List
from datetime import date

from bot.misc import logger
from bot.models import User
from bot.text import CfschTexts, AdminText
from bot.markups.inline_markups import BrandInlineBuilder
from bot.models import User
from bot.controllers.user import user_exists

# VALIDATORS
def cost_validator(text: str | None = None) -> str | None:
    if text is None:
        return None
    res = re.sub(r'[^-0-9]', '', text)
    res = re.match(r'\d+-\d+', res)
    if res is None:
        return None
    res = res.group(0)
    tmp = [int(i) for i in res.split('-')]
    start, end = tmp[0], tmp[1]
    if start < 0 or start > 100_000_000:
        return None
    if end < 10000 or end > 100_000_000:
        return None
    if start >= end:
        return None
    return res

def mileage_validator(text: str | None = None) -> str | None:
    if text is None:
        return None
    res = re.sub(r'[^0-9]', '', text)
    res = re.match(r'\d+', res)
    if res is None:
        return None
    res = res.group(0)
    if int(res) < 0 or int(res) > 1_000_000_000:
        return None
    return res

def year_release_validator(text: str | None = None) -> str | None:
    if text is None:
        return None
    res = re.sub(r'[^-0-9]', '', text)
    res = re.match(r'\d{4}-\d{4}', res)
    if res is None:
        return None
    res = res.group(0)
    tmp = [int(i) for i in res.split('-')]
    start, end = tmp[0], tmp[1]
    if start < 1800 or start > date.today().year:
        return None
    if end < 1800 or end > date.today().year:
        return None
    if start >= end:
        return None
    return res

# def count_owners_validator(text: str | None = None) -> str | None:
#     if text is None:
#         return None
#     res = re.sub(r'[^0-9]', '', text)
#     res = re.match(r'\d{1,2}', res)
#     if res is None:
#         return None
#     res = res.group(0)
#     if int(res) < 1 or int(res) > 99:
#         return None
#     return res

def brand_validator(text: str | None = None) -> str | None:
    return text

def odds_rate_validator(text: str | None = None) -> str | None:
    if text is None:
        return None
    res = re.sub(r'[^0-9]', '', text)
    res = re.match(r'\d+', res)
    if res is None:
        return None
    res = res.group(0)
    if int(res) < 0 or int(res) > 100_000_000:
        return None
    return res

cfsch_messages = {
    'cost': {
        'text': CfschTexts.cost,
        'text_error': CfschTexts.cost_error,
        'validator': cost_validator,
    },
    'region': {
        'text': CfschTexts.region,
        'text_error': None,
        'validator': None,
    },
    'mileage': {
        'text': CfschTexts.mileage,
        'text_error': CfschTexts.mileage_error,
        'validator': mileage_validator,
    },
    'year_release': {
        'text': CfschTexts.year_release,
        'text_error': CfschTexts.year_release_error,
        'validator': year_release_validator,
    },
    'count_owners': {
        'text': CfschTexts.count_owners,
        'text_error': None,
        'validator': None,
    },
    'brand': {
        'text': CfschTexts.brand,
        'text_error': None,
        'validator': None,
    },
    'odds': {
        'text': CfschTexts.odds,
        'text_error': None,
        'validator': None,
    },
    'odds_rate': {
        'text': CfschTexts.odds_rate,
        'text_error': CfschTexts.odds_rate_error,
        'validator': odds_rate_validator,
    },
}

async def validator_user_id(text: str | None = None) -> int | None:
    if text is None:
        return None
    res = re.sub(r'[^-0-9]', '', text)
    res = re.match(r'\d+', res)
    if res is None:
        return None
    res = res.group(0)
    user_id = int(res)
    user = await user_exists(user_id)
    if user is None:
        return None
    else:
        return user_id

admin_messages = {
    'admin_add_rm': {
        'text': AdminText.add_rm_admin,
        'text_error': None,
    },
    'admin_input_id': {
        'text': AdminText.input_id,
        'text_error': AdminText.input_id_error,
    },
    'admin_confirm': {
        'text': AdminText.confirm_admin,
        'text_error': None,
    },
    #______________________________________________
    'user_add_rm_permission': {
        'text': AdminText.add_rm_user_permission,
        'text_error': None,
    },
    'user_input_id': {
        'text': AdminText.input_id,
        'text_error': AdminText.input_id_error,
    },
    'user_input_timeframe': {
        'text': AdminText.choose_timeframe,
        'text_error': None,
    },
    'user_confirm': {
        'text': AdminText.confirm_user,
        'text_error': None,
    }
}

async def delete_reply_markups(msg: Message) -> bool:
    try:
        system_msg = await msg.answer(text='systems: delete reply', reply_markup=ReplyKeyboardRemove(), disable_notification=True, disable_web_page_preview=True)
        await system_msg.delete()
        return True
    except:
        logger.exception('delete_reply_markups ERROR')
        return False

def is_can_subscribe(user:User) -> str | None:
    """
    return None if can subscribe
    else return why not
    """
    if user.notifi_status:
        return 'Вы уже подписаны'
    if not user.filters:
        return 'Нужно настроить фильтры'
    if user.demo_status:
        if user.demo_counter >= 10:
            return 'Демо версия закончилась'
        else:
            return None
    if date.today() > user.full_time_end:
        return 'Время действия полной версии закончилось'
    else:
        return None

# {'cost': 'all', 'odds': 'low', 'brand': {'ГАЗ': 'ГАЗ'}, 'region': 'sankt-peterburg', 'mileage': 'all', 'odds_rate': '0', 'count_owners': 'all', 'year_release': 'all'}
async def save_filters(user:User, data:Dict[str, Any] | None = None) -> bool:
    if data is not None:
        try:
            names_key = [key for key in cfsch_messages.keys()]
            remove_keys_list:List[str] = []
            for key in data.keys():
                if key not in names_key:
                    remove_keys_list.append(key)
            while len(remove_keys_list) != 0:
                remove_key = remove_keys_list.pop()
                data.pop(remove_key)
        except (ValueError, TypeError, RecursionError):
            logger.error('Invalid Data in save filters')
            return False
        try:
            data['brand'] = [key for key in data['brand'].keys()]
        except:
            logger.error('Invalid Data, no key brand')
            return False
    else:
        data = {k:'all' for k, v in cfsch_messages.items()}
        data.pop('odds_rate')
        data['brand'] = [i for i in BrandInlineBuilder.car_brands]
        data['brand'].append('all_other')
    user.filters = data
    await user.save(update_fields=['filters'])
    return True
    

