from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List
import Types

error_occured = "<b>Ой, произошла ошибка. Я уже сообщил о ней разработчику</b>"

loading_data = """
<i>Подождите, получаю данные...</i>
"""

# ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА
start_message = """
<b>Доброе утро! Я - бот системы расписания Лицея</b>

Я могу отправлять вам уведомления об изменениях в расписании классов и учителей.
Хотите настроить?
"""

start_keyboard = InlineKeyboardMarkup() \
    .add(InlineKeyboardButton("Давай настроим", callback_data="start:setup"))
    
start_setup_message = """
<b>Класс! Вы хотите отслеживать изменения в расписании для класса или для учителя?</b>
"""

start_setup_keyboard = InlineKeyboardMarkup() \
    .add(InlineKeyboardButton("Для класса", callback_data="start:setup:class"), InlineKeyboardButton("Для учителя", callback_data="start:setup:teacher"))
    
start_setup_back_button = InlineKeyboardButton("< Назад", callback_data="start:setup")
    
start_setup_class_message = """
<b>Выберите класс, расписание для которого хотите отслеживать</b>
"""

start_setup_teacher_message = """
<b>Выберите учителя, расписание для которого хотите отслеживать</b>
"""

start_setup_class_complete = lambda a: f"<b>Класс! Теперь я буду отправлять вам уведомления об изменениях в расписании для класса {a}</b>\n\nВы можете настроить это поведение, используя /settings"
start_setup_teacher_complete = lambda a: f"<b>Класс! Теперь я буду отправлять вам уведомления об изменениях в расписании для учителя {a}</b>\nВы можете настроить это поведение, используя /settings"

# НАСТРОЙКИ
def settings(subscriptions: List[Types.Subscription], classes: Types.OptionCollection, teachers: Types.OptionCollection):
    text = "<b>Мои подписки:</b>\n"
    
    if len(subscriptions) == 0:
        text += "\nУ вас нет активных подписок"
    else:
        for sub in subscriptions:
            matched = list(filter(lambda a: a.id == sub.id, (classes if sub.type == "class" else teachers)))
            text += "\n<нет данных>" if len(matched) == 0 else f"\n{matched[0].name}"
            
    return text

settings_keyboard = InlineKeyboardMarkup() \
    .add(InlineKeyboardButton("Добавить подписку", callback_data="settings:add")) \
    .add(InlineKeyboardButton("Управление подписками", callback_data="settings:manage"))
    
settings_add_message = """
<b>Вы хотите отслеживать изменения в расписании для класса или для учителя?</b>
"""

settings_add_keyboard = InlineKeyboardMarkup() \
    .add(InlineKeyboardButton("Для класса", callback_data="settings:add:class"), InlineKeyboardButton("Для учителя", callback_data="settings:add:teacher"))
    
settings_add_back_button = InlineKeyboardButton("< Назад", callback_data="settings:add")
    
settings_add_class_message = start_setup_class_message
settings_add_teacher_message = start_setup_teacher_message

settings_add_class_complete = lambda a: f"<b>Вы подписались на изменения в расписании для класса {a}</b>"
settings_add_teacher_complete = lambda a: f"<b>Вы подписались на изменения в расписании для учителя {a}</b>"

return_to_settings_keyboard = InlineKeyboardMarkup() \
    .add(InlineKeyboardButton("< Вернуться в настройки", callback_data="settings"))
    
settings_manage_message = "<b>Выберите подписку</b>"

settings_manage_class = lambda a: f"<b>Выбрана подписка на изменение расписания для класса {a}</b>"
settings_manage_teacher = lambda a: f"<b>Выбрана подписка на изменение расписания для учителя {a}</b>"

settings_manage_keyboard = lambda type, id: InlineKeyboardMarkup() \
    .add(InlineKeyboardButton("Отписаться", callback_data=f"settings:manage:{type}:{id}:delete")) \
    .add(InlineKeyboardButton("< Назад", callback_data="settings:manage"))
    
settings_manage_deleted_class_message = lambda a: f"<b>Вы отписались от уведомлений о изменении расписания для класса {a}</b>"
settings_manage_deleted_teacher_message = lambda a: f"<b>Вы отписались от уведомлений о изменении расписания для учителя {a}</b>"

settings_manage_deleted_keyboard = InlineKeyboardMarkup() \
    .add(InlineKeyboardButton("< Назад", callback_data="settings:manage"))
