from aiogram.utils.formatting import Bold, Text, as_key_value, as_marked_section
from aiogram.methods import SendMessage

from datetime import date
import re
import asyncio

from bot.models import AdvertModel
from bot.models import User
from bot.misc import bot, logger
from bot.markups.inline_markups import BrandInlineBuilder

async def distribution(data:dict):
    async def validate_and_send(user:User, model:AdvertModel) -> str:
        if not await is_get_user(user=user):
            return f'Not user {user.full_name}'
        if not await is_get_filter(user=user, model=model):
            return f'Not filter {user.full_name}'
        notifi_status = await send_notifi(user=user, model=model)
        if notifi_status:
            user.demo_counter += 1
            await user.save(update_fields=['demo_counter'])
            return f'SUCSESS notifi {user.full_name}'
        else:
            return f'Exception notifi {user.full_name}'

    model = AdvertModel()
    model.from_json(data)
    users = await User.all()
    tasks = [asyncio.create_task(validate_and_send(user=user, model=model)) for user in users]
    for future in asyncio.as_completed(tasks):
        res = await future
        logger.info(res)

        

async def send_notifi(user:User, model:AdvertModel) -> bool:
    title = Bold('Новое обьявление\n')
    rows = []

    location = model.location.copy().popitem()
    rows.append(as_key_value('Город', re.sub(r'\s', ' ', location[1])))
    rows.append(Text('\n'))

    rows.append(as_key_value('Цена в обьявлении', f"{model.price:_} руб.".replace("_", " ")))
    if model.price < model.down_price:
        d = model.down_price - model.price
        f = f"{d:_}".replace("_", " ")
        rows.append(Bold(f'Цена ниже на {f} рублей по сравнению с нижней оценкой от Авито.'))
    rows.append(Text('\n'))


    rows.append(as_key_value('Название', re.sub(r'\s', ' ', model.advert_name)))
    name_conf_list = [
        'Год выпуска',
        'Пробег, км',
        'Модификация',
        'Объём двигателя, л',
        'Тип двигателя',
        'Коробка передач',
        'Привод',
        'Комплектация',
        'Тип кузова',
        'Цвет',
        'Руль',
    ]
    for name in name_conf_list:
        try:
            value = model.properties_list[name]
        except:
            continue
        rows.append(as_key_value(name, value))
    rows.append(Text('\n'))

    try:
        value = model.properties_list['Владельцев по ПТС']
        rows.append(as_key_value('Владельцев по ПТС', value))
    except:
        pass
    rows.append(as_key_value('Ссылка на обьявление', model.link))

    message = as_marked_section(
        title,
        *rows,
        marker="",
    )
    try:
        await SendMessage(chat_id=user.chat_id, **message.as_kwargs()).as_(bot=bot)
        return True
    except:
        logger.exception('ERROR Send Notifier')
        return False
        

async def is_get_user(user:User) -> bool:
    if user.chat_id is None: # Рудимент миграции
        return False
    if user.notifi_status:
        if user.demo_status:
            if user.demo_counter >= 10:
                return False
            else:
                return True
        if date.today() > user.full_time_end:
            user.notifi_status = False
            await user.save(update_fields='notifi_status')
            return False
        else:
            return True
    else:
        return False
    
async def is_get_filter(user:User, model:AdvertModel) -> bool:
    filters = user.filters
    assert(type(filters) is dict)
    for key, value in filters.items():
        if value == 'all':
            continue
        if key == 'cost':
            assert(type(value) is str)
            [begin, end] = value.split('-')[:2]
            begin, end = int(begin.strip()), int(end.strip())
            if int(model.price) < begin or int(model.price) > end:
                return False
        if key == 'region':
            location = model.location.copy().popitem()
            if location[0] != 'moskva' and location[0] != 'sankt-peterburg':
                return False
        if key == 'mileage':
            try:
                milage:str = model.properties_list['Пробег, км']
                milage = int(re.sub(r'[^0-9]', '', milage))
            except:
                return False
            if milage > int(value):
                return False
        if key == 'year_release':
            try:
                year_release:str = model.properties_list['Год выпуска']
                year_release = int(re.sub(r'[^0-9]', '', year_release))
            except:
                return False
            assert(type(value) is str)
            [begin, end] = value.split('-')[:2]
            begin, end = int(begin.strip()), int(end.strip())
            if year_release < begin or year_release > end:
                return False
        if key == 'count_owners':
            try:
                count_owners:str = model.properties_list['Год выпуска']
                count_owners = int(re.sub(r'[^0-9]', '', count_owners))
            except:
                if int(value) == '4':
                    return False
            assert(type(value) is str)
            if int(value) < count_owners:
                return False
        if key == 'brand':
            if len(value) < len(BrandInlineBuilder.car_brands) + 1:
                assert(type(value) is list)
                is_include_all_other:bool = False
                try:
                    value.remove('all_other')
                    is_include_all_other = True
                except ValueError:
                    pass
                for tamplate in value:
                    assert(type(tamplate) is str)
                    if tamplate in model.advert_name:
                        break
                else:
                    if is_include_all_other:
                        for tamplate in BrandInlineBuilder.car_brands:
                            if tamplate in model.advert_name:
                                return False
                    else:
                        return False
        if key == 'odds':
            rate = model.down_price - model.price
            if rate < int(filters['odds_rate']):
                return False
    return True
