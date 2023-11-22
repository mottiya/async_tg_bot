from typing import Optional
from aiogram.filters.state import StatesGroup, State
  
class ConfSearchState(StatesGroup):
    cost = State()
    region = State()
    mileage = State()
    year_release = State()
    count_owners = State()
    brand = State()
    odds = State()
    odds_rate = State()
    
    def start() -> State:
        return ConfSearchState.cost

    def next(cur_state:Optional[str]) -> Optional[State]:
        if cur_state is None:
            return ConfSearchState.cost
        cur_state = cur_state.replace('ConfSearchState:', '')
        if cur_state == 'cost':
            return ConfSearchState.region
        if cur_state == 'region':
            return ConfSearchState.mileage
        if cur_state == 'mileage':
            return ConfSearchState.year_release
        if cur_state == 'year_release':
            return ConfSearchState.count_owners
        if cur_state == 'count_owners':
            return ConfSearchState.brand
        if cur_state == 'brand':
            return ConfSearchState.odds
        if cur_state == 'odds':
            return ConfSearchState.odds_rate
        if cur_state == 'odds_rate':
            return None
        return None
        

    def pref(cur_state:Optional[str]) -> Optional[State]:
        if cur_state is None:
            return None
        cur_state = cur_state.replace('ConfSearchState:', '')
        if cur_state == 'cost':
            return None
        if cur_state == 'region':
            return ConfSearchState.cost
        if cur_state == 'mileage':
            return ConfSearchState.region
        if cur_state == 'year_release':
            return ConfSearchState.mileage
        if cur_state == 'count_owners':
            return ConfSearchState.year_release
        if cur_state == 'brand':
            return ConfSearchState.count_owners
        if cur_state == 'odds':
            return ConfSearchState.brand
        if cur_state == 'odds_rate':
            return ConfSearchState.odds
        return None

class AdminState(StatesGroup):
    admin_add_rm = State()
    admin_input_id = State()
    admin_confirm = State()

    user_add_rm_permission = State()
    user_input_id = State()
    user_input_timeframe = State()
    user_confirm = State()

    def next(cur_state:Optional[str]) -> Optional[State]:
        if cur_state is None:
            return None
        cur_state = cur_state.replace('AdminState:', '')

        if cur_state == 'admin_add_rm':
            return AdminState.admin_input_id
        if cur_state == 'admin_input_id':
            return AdminState.admin_confirm
        if cur_state == 'admin_confirm':
            return None
        
        if cur_state == 'user_add_rm_permission':
            return AdminState.user_input_id
        if cur_state == 'user_input_id':
            return AdminState.user_input_timeframe
        if cur_state == 'user_input_timeframe':
            return AdminState.user_confirm
        if cur_state == 'user_confirm':
            return None
        
        return None

    def pref(cur_state:Optional[str]) -> Optional[State]:
        if cur_state is None:
            return None
        cur_state = cur_state.replace('AdminState:', '')

        if cur_state == 'admin_add_rm':
            return None
        if cur_state == 'admin_input_id':
            return AdminState.admin_add_rm
        if cur_state == 'admin_confirm':
            return AdminState.admin_input_id
        
        if cur_state == 'user_add_rm_permission':
            return None
        if cur_state == 'user_input_id':
            return AdminState.user_add_rm_permission
        if cur_state == 'user_input_timeframe':
            return AdminState.user_input_id
        if cur_state == 'user_confirm':
            return AdminState.user_input_timeframe
        
        return None
