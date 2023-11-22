from bot.misc import admin_ref, max_demo_notifi
from bot.models import User
from bot.markups.inline_markups import BrandInlineBuilder

# MAIN PAGE
main_page = 'Главное меню'

# LK
lk = 'Личный кабинет'
support = f'Напишите сюда {admin_ref}, чтобы связаться с поддержкой'
tutorial = 'Для того чтобы получать предложения о доступных автомобилях, вам необходимо настроить параметры поиска в разделе "Настройки". Укажите критерии и характеристики автомобилей, которые вам интересны. Важно отметить, что AVTOPAD проводит анализ только недавно опубликованных объявлений, а не предлагает результаты по уже опубликованным объявлениям.'

def get_info_tarif(demo_status:bool, tarif_end, count_notifi:int | None = None):
    return f'Ваш тариф: {"Free" if demo_status else "Full"}\n{"Получено обьявлений" if demo_status else "Срок действия до"} {f"{count_notifi}/{max_demo_notifi}" if demo_status else str(tarif_end)}\n\nДоступные тарифы:\nНа неделю: 1р\nНа месяц: 5р\nНа Три месяца: 7р'

def get_info_pay(period:str):
    if period == '1w':
        return f'Чтобы воспользоваться тарифом на неделю оплатите 1р на карту 666\n\nПосле оплаты, направьте квитанцию в чат поддержки {admin_ref}'
    if period == '1m':
        return f'Чтобы воспользоваться тарифом на месяц оплатите 5р на карту 666\n\nПосле оплаты, направьте квитанцию в чат поддержки {admin_ref}'
    if period == '3m':
        return f'Чтобы воспользоваться тарифом на три месяца оплатите 7р на карту 666\n\nПосле оплаты, направьте квитанцию в чат поддержки {admin_ref}'

# SUBSCRIBE AND UNSUBSCRIBE
subscribe = 'Вы подписались на уведомления'
unsubscribe = 'Вы отписались от уведомлений'

# CONFIG SEARCH
config_search_main = 'Настройка поиска'
empty_filtres = 'У вас пока не настроены фильтры'
error_filters = 'Произошла ошибка сохранения фильтров, попробуйте позже'

all_filters = 'Вы уверены, что хотите сбросить все текущие фильтры и получать все обьявления?'

class CfschTexts:
    cost = 'Напишите границы стоимости автомобиля в формате 500 000 - 1 000 000 или выберите любую стоимость'
    cost_error = 'Ошибка, напишите границы стоимости в числовом формате указав диапазон цен через тире, пример: 500 000 - 1 000 000'

    region = 'Выберите регион'

    mileage = 'Напишите только число до какого пробега рассматривать автомобили'
    mileage_error = 'Ошибка, напишите цифрами пробег, не используя буквы и другие символы'

    year_release = 'Напишите год выпуска автомобиля через тире, пример: 2005 - 2010'
    year_release_error = 'Ошибка, напишите год выпуска через тире, пример: 2005 - 2010'

    count_owners = 'Выберите до какого количества владельцев рассматривать автомобили'
    # count_owners_error = 'Ошибка'

    brand = 'Выберите марки авто которые вам интересны.\nЧтобы отменить выбор, нажмите на марку ещё раз.'

    odds = 'Вы хотите получать автомобили, чья стоимость по рынку или ниже рынка?'

    odds_rate = 'Укажите сумму на которую автомобиль должен быть ниже рынка, отправьте 0 чтобы выбрать все автомобили которые ниже оценки авито'
    odds_rate_error = 'Ошибка, надо указать только число, попробуйте ещё раз указать сумму на которую автомобиль должен быть ниже рынка, отправьте 0 чтобы выбрать все автомобили которые ниже оценки авито'

from aiogram.utils.formatting import Bold,  Text, as_marked_section, as_key_value
def get_filtres(user:User | None = None) -> Text:
    if user is None:
        return Text(empty_filtres)
    filters = user.filters
    if filters is None:
        return Text(empty_filtres)
    assert(type(filters) is dict)
    title = Bold("Текущие фильтры\n")
    body = [None for _ in range(7)]
    for key, value in filters.items():
        if key == 'cost':
            body[0] = as_key_value(
                'Ценовой сегмент', f'{value} руб' if value != 'all' else 'Все цены'
            )
        if key == 'region':
            if value == 'moskva':
                value = 'Москва'
            if value == 'sankt-peterburg':
                value = 'СПБ'
            if value == 'all':
                value = 'Все регионы'
            body[2] = as_key_value(
                'Регион', value
            )
        if key == 'mileage':
            body[4] = as_key_value(
                'Пробег', f'до {value} км' if value != 'all' else 'Любой'
            )
        if key == 'year_release':
            body[3] = as_key_value(
                'Год выпуска', value if value != 'all' else 'Любой'
            )
        if key == 'count_owners':
            if value == 'all':
                value = 'Любое'
            elif value == '4':
                value = f'от {value} владельцев'
            else:
                value = f'до {value} владельцев'
            body[5] = as_key_value(
                'Кол-во владельцев', value
            )
        if key == 'brand':
            if len(value) >= len(BrandInlineBuilder.car_brands) + 1:
                value = 'Все марки'
            else:
                try:
                    assert(type(value) is list)
                    value.remove('all_other')
                    all_other = 'Все остальные (кроме невыбранных)'
                    if len(value) != 0:
                        all_other = ' и ' + all_other
                except ValueError:
                    all_other = ''
                value = ', '.join(value) + all_other
            body[1] = as_key_value(
                'Марки', value
            )
        if key == 'odds':
            if value == 'all':
                value = 'Все по рынку и ниже'
            if value == 'low':
                if int(filters['odds_rate']) == 0:
                    value = 'Только ниже рынка'
                else:
                    value = f'Ниже рынка на {filters["odds_rate"]} руб'
            body[6] = as_key_value(
                'Разница', value
            )
    filters_str = as_marked_section(
            title,
            *body,
            marker="- ",
        )
    return filters_str

# COMMANDS
start = 'Добро пожаловать в AVTOPAD! Этот бот поможет вам находить самые ликвидные автомобили, быстрее всех конкурентов.'
help_text = f'{start}\n{tutorial}'

# ADMIN
greet_admin = 'Админ панель'
error_add_rm = 'Ошибка! Не удалось найти пользователя'
class AdminText:
    add_rm_admin = 'Добавить/Удалить админа'
    add_rm_user_permission = 'Добавить/Удалить пользователя'
    show_all_users = 'Показать всех пользователей'

    input_id = 'Введите ID Телеграмм, кого хотите добавить/удалить'
    input_id_error = 'Такого ID нет в базе зарегистрированных пользователей, попробуйте еще раз'
    choose_timeframe = 'Выберите длительность подписки'

    confirm_user = 'Добавить/удалить пользователя id {user_id} на {timeframe}?'
    confirm_admin = 'Добавить/удалить админа id {user_id}?'

    success_user = 'Вы успешно добавили/удалили пользователя с полным тарифом'
    success_admin = 'Вы успешно добавили/удалили администратора'

# CAP
cap = f'Я вас не понимаю, если есть вопросы напишите в поддержку - {admin_ref}'
