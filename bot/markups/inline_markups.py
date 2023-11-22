from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from typing import Any, Dict, List

def get_keyboard(buttons_data:List[List[List[str]]] = []) -> InlineKeyboardMarkup:
    buttons = []
    for row in buttons_data:
        buttons.append([InlineKeyboardButton(text=button[0], callback_data=button[1]) for button in row])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def lk_choose_tarif() -> InlineKeyboardMarkup:
    buttons_data = [
        [
            ['Неделя', 'lk_1week'],
            ['Месяц', 'lk_1mounth'],
            ['Три месяца', 'lk_3mounth']
        ]
    ]
    return get_keyboard(buttons_data)

def all_filters() -> InlineKeyboardMarkup:
    buttons_data = [
        [
            ['ДА', 'all_filters_agree'],
            ['Отмена', 'all_filters_cancel']
        ]
    ]
    return get_keyboard(buttons_data)

class CfschButtons:
    main_page = InlineKeyboardButton(text='🌀 Главная', callback_data='cfsch_main_page')
    back = InlineKeyboardButton(text='⬅ Назад', callback_data='cfsch_back')

    cost_all = InlineKeyboardButton(text='Любая стоимость', callback_data='cfsch_cost_all')

    region_moskva = InlineKeyboardButton(text='Москва', callback_data='cfsch_region_moskva')
    region_spb = InlineKeyboardButton(text='СПБ', callback_data='cfsch_region_spb')
    region_all = InlineKeyboardButton(text='Все регионы', callback_data='cfsch_region_all')

    mileage_all = InlineKeyboardButton(text='Любой пробег', callback_data='cfsch_mileage_all')

    year_release_all = InlineKeyboardButton(text='Любой год', callback_data='cfsch_year_release_all')

    count_owners_1 = InlineKeyboardButton(text='Один владелец', callback_data='cfsch_count_owners_1')
    count_owners_2 = InlineKeyboardButton(text='Не более двух', callback_data='cfsch_count_owners_2')
    count_owners_3 = InlineKeyboardButton(text='Не более трех', callback_data='cfsch_count_owners_3')
    count_owners_4 = InlineKeyboardButton(text='Четыре и более', callback_data='cfsch_count_owners_4')
    count_owners_all = InlineKeyboardButton(text='Любое количество', callback_data='cfsch_count_owners_all')

    odds_all = InlineKeyboardButton(text='По рынку и ниже', callback_data='cfsch_odds_all')
    odds_low = InlineKeyboardButton(text='Только ниже рынка', callback_data='cfsch_odds_low')

    odds_rate = None,

class AdminButtons:
    cancel = InlineKeyboardButton(text='Отмена', callback_data='admin_cancel')
    back = InlineKeyboardButton(text='⬅ Назад', callback_data='admin_back')

    add = InlineKeyboardButton(text='Добавить', callback_data='admin_add')
    rm = InlineKeyboardButton(text='Удалить', callback_data='admin_rm')

    timeframe_1w = InlineKeyboardButton(text='Неделя', callback_data='admin_timeframe_1w')
    timeframe_1m = InlineKeyboardButton(text='Месяц', callback_data='admin_timeframe_1m')
    timeframe_3m = InlineKeyboardButton(text='Три месяца', callback_data='admin_timeframe_3m')

    confirm = InlineKeyboardButton(text='Подтвердить', callback_data='admin_confirm')

async def state_inline_markups(state: FSMContext) -> InlineKeyboardMarkup:
    cur_state = await state.get_state()
    assert(cur_state is not None)
    cur_state = cur_state.replace('ConfSearchState:', '')
    cur_state = cur_state.replace('AdminState:', '')
    #_______________________________________________________________________________________________________________________________
    if cur_state == 'cost':
        return InlineKeyboardMarkup(inline_keyboard=[[CfschButtons.cost_all],
                                                     [CfschButtons.main_page, CfschButtons.back]])
    if cur_state == 'region':
        return InlineKeyboardMarkup(inline_keyboard=[[CfschButtons.region_moskva, CfschButtons.region_spb, CfschButtons.region_all],
                                                     [CfschButtons.main_page, CfschButtons.back]])
    if cur_state == 'mileage':
        return InlineKeyboardMarkup(inline_keyboard=[[CfschButtons.mileage_all],
                                                     [CfschButtons.main_page, CfschButtons.back]])
    if cur_state == 'year_release':
        return InlineKeyboardMarkup(inline_keyboard=[[CfschButtons.year_release_all],
                                                     [CfschButtons.main_page, CfschButtons.back]])
    if cur_state == 'count_owners':
        return InlineKeyboardMarkup(inline_keyboard=[[CfschButtons.count_owners_1, CfschButtons.count_owners_2],
                                                     [CfschButtons.count_owners_3, CfschButtons.count_owners_4],
                                                     [CfschButtons.count_owners_all],
                                                     [CfschButtons.main_page, CfschButtons.back]])
    if cur_state == 'brand':
        return BrandInlineBuilder(await state.get_data()).get_keyboard()
    if cur_state == 'odds':
        return InlineKeyboardMarkup(inline_keyboard=[[CfschButtons.odds_all, CfschButtons.odds_low],
                                                     [CfschButtons.main_page, CfschButtons.back]])
    if cur_state == 'odds_rate':
        return InlineKeyboardMarkup(inline_keyboard=[[CfschButtons.main_page, CfschButtons.back]])
    #_______________________________________________________________________________________________________________________________
    if cur_state == 'admin_add_rm':
        return InlineKeyboardMarkup(inline_keyboard=[[AdminButtons.add, AdminButtons.rm], [AdminButtons.back, AdminButtons.cancel]])
    if cur_state == 'admin_input_id':
        return InlineKeyboardMarkup(inline_keyboard=[[AdminButtons.back, AdminButtons.cancel]])
    if cur_state == 'admin_confirm':
        return InlineKeyboardMarkup(inline_keyboard=[[AdminButtons.confirm], [AdminButtons.back, AdminButtons.cancel]])

    if cur_state == 'user_add_rm_permission':
        return InlineKeyboardMarkup(inline_keyboard=[[AdminButtons.add, AdminButtons.rm], [AdminButtons.back, AdminButtons.cancel]])
    if cur_state == 'user_input_id':
        return InlineKeyboardMarkup(inline_keyboard=[[AdminButtons.back, AdminButtons.cancel]])
    if cur_state == 'user_input_timeframe':
        return InlineKeyboardMarkup(inline_keyboard=[[AdminButtons.timeframe_1w, AdminButtons.timeframe_1m, AdminButtons.timeframe_3m], [AdminButtons.back, AdminButtons.cancel]])
    if cur_state == 'user_confirm':
        return InlineKeyboardMarkup(inline_keyboard=[[AdminButtons.confirm], [AdminButtons.back, AdminButtons.cancel]])

class BrandInlineBuilder:

    car_brands = [
        'Audi',
        'BMW',
        'Chery',
        'Chevrolet',
        'Ford',
        'Haval',
        'Honda',
        'Hyundai',
        'Kia',
        'Mazda',
        'Mercedes-Benz',
        'Mitsubishi',
        'Nissan',
        'Opel',
        'Renault',
        'Skoda',
        'Toyota',
        'Volkswagen',
        'ВАЗ (LADA)',
        'ГАЗ',
    ]

    systems = [
        'all_other',
        'all',
        'approve',
    ]
    
    helps = (car_brands + systems)[:-1]

    def __init__(self, active_buttons:Dict[str, Any] = {}) -> None:
        self.active_buttons = active_buttons

    def get_brand_config_buttons(self) -> List[List[List[str]]]:
        p = '✅ '
        active_buttons:Dict[str, str] = self.active_buttons.get('brand')
        if active_buttons is None:
            active_buttons = {}

        __brand = [[]]
        counter = 0
        for b in range(len(self.car_brands)):
            if len(__brand[counter]) >= 3:
                __brand.append([])
                counter += 1
            __brand[counter].append([f'{p if active_buttons.get(self.car_brands[b]) is not None else ""}{self.car_brands[b]}', f'cfsch_brand_{self.car_brands[b]}'])

        __brand[-1].append([f'{p if active_buttons.get("all_other") is not None else ""}Все остальные', f'cfsch_brand_{self.systems[0]}'])

        __brand.append([])
        __brand[-1].append([f'{p if len(active_buttons) >= len(self.helps) - 1 else ""}Вообще все', f'cfsch_brand_{self.systems[1]}'])
        __brand[-1].append([f'Подтвердить выбор ->', f'cfsch_brand_{self.systems[2]}'])
        return __brand

    def get_buttons(self) -> List[List[List[InlineKeyboardButton]]]:
        buttons_data = self.get_brand_config_buttons()
        buttons = []
        for row in buttons_data:
            buttons.append([InlineKeyboardButton(text=button[0], callback_data=button[1]) for button in row])
        return buttons
    
    def get_keyboard(self) -> InlineKeyboardMarkup:
        keyboard = self.get_buttons()
        keyboard.append([CfschButtons.main_page, CfschButtons.back])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
