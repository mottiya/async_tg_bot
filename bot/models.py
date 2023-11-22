from enum import Enum

from tortoise.models import Model
from tortoise import fields

from config import DEFAULT_ADMIN

class NameEnum(Enum):
    advert_name = 'Название'
    link = 'Ссылка'
    id = 'ID'
    price = 'Цена'
    down_price = 'Нижняя оценка'
    up_price = 'Верхняя оценка'
    location = 'Регион'
    properties_list = 'Характеристики'

class AdvertModel():

    def __init__(self) -> None:
        self.advert_name = None
        self.link = None
        self.id = None
        self.price = None
        self.down_price = None
        self.up_price = None
        self.location = None
        self.properties_list = None

    def from_json(self, data:dict):
        try:
            self.advert_name = data[NameEnum.advert_name.value]
        except KeyError:
            pass
        try:
            self.link = data[NameEnum.link.value]
        except KeyError:
            pass
        try:
            self.id = data[NameEnum.id.value]
        except KeyError:
            pass
        try:
            self.price = data[NameEnum.price.value]
        except KeyError:
            pass
        try:
            self.down_price = data[NameEnum.down_price.value]
        except KeyError:
            pass
        try:
            self.up_price = data[NameEnum.up_price.value]
        except KeyError:
            pass
        try:
            self.location = data[NameEnum.location.value]
        except KeyError:
            pass
        try:
            self.properties_list = data[NameEnum.properties_list.value]
        except KeyError:
            pass
    
    def __str__(self) -> str:
        diction = {
            'Название':self.advert_name,
            'Ссылка':self.link,
            'ID':self.id,
            'Цена':self.price,
            'Нижняя оценка':self.down_price,
            'Верхняя оценка':self.up_price,
            'Регион':self.location,
            'Характеристики':self.properties_list,
        }
        return str(diction)



class User(Model):
    user_id = fields.BigIntField(unique=True)
    chat_id = fields.BigIntField()
    username = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255)
    admin_status = fields.BooleanField(default=False)
    demo_status = fields.BooleanField(default=True)
    demo_counter = fields.IntField(default=0)
    full_time_start = fields.DateField(null=True)
    full_time_end = fields.DateField(null=True)
    notifi_status = fields.BooleanField(default=False)
    filters = fields.JSONField(null=True, default=None)
    

    class Meta:
        table = "users"

    def __str__(self):
        res = f"user_id: {self.user_id}\n"
        res += f"chat_id: {self.chat_id}\n"
        res += f"username: {self.username}\n"
        res += f"full_name: {self.full_name}\n"
        res += f"admin_status: {self.admin_status}\n"
        res += f"demo_status: {self.demo_status}\n"
        res += f"demo_counter: {self.demo_counter}\n"
        res += f"full_time_start: {self.full_time_start}\n"
        res += f"full_time_end: {self.full_time_end}\n"
        res += f"notifi_status: {self.notifi_status}\n"
        res += f"filters: {self.filters}\n"
        return res
    
    async def is_admin(self):
        if self.user_id == DEFAULT_ADMIN:
            if not self.admin_status:
                self.admin_status = True
                await self.save(update_fields=['admin_status'])
        return self.admin_status
