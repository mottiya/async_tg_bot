from typing import List
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def __get_keyboard(buttons_data:List[List[str]] = []) -> ReplyKeyboardMarkup:
    buttons = []
    for row in buttons_data:
        buttons.append([KeyboardButton(text=button) for button in row])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# MAIN PAGE
def main_markup(notifi_status:bool) -> ReplyKeyboardMarkup:
    buttons_data = [
        ['Личный кабинет', 'Настройка поиска'],
        ['Приостановить отправку уведомлений' if notifi_status else 'Подписаться на уведомления'],
    ]
    return __get_keyboard(buttons_data)

# LK
def lk_markup() -> ReplyKeyboardMarkup:
    buttons_data = [
        ['Поддержка', 'Информация о тарифе'],
        ['Туториал', '🌀 Главная'],
    ]
    return __get_keyboard(buttons_data)

# CONFIG SEARCH
def config_search_markup():
    buttons_data = [
        ['Текущие фильтры', 'Настроить фильтры'],
        ['Получать все обьявления', '🌀 Главная'],
    ]
    return __get_keyboard(buttons_data)

# ADMIN
def admin_main_murkups():
    buttons_data = [
        ['Добавить/Удалить пользователя', 'Добавить/Удалить админа'],
        ['Показать всех пользователей', '🌀 Главная'],
    ]
    return __get_keyboard(buttons_data)

def add_rm():
    buttons_data = [
        ['Добавить', 'Удалить'],
        ['⬅️ Назад'],
    ]
    return __get_keyboard(buttons_data)