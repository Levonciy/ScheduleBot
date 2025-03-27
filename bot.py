import traceback
from telebot import types as tg

import actions
import context
import error_reporter
from locales import ru
import Types

bot = context.bot

# ПЕРВОНАЧАЛЬНАЯ НАСТРОЙКА
@bot.message_handler(["start"], func=lambda a: len(list(filter(lambda b: b.receiver_id == a.chat.id, context.config.subscriptions))) == 0)
async def start(message: tg.Message):
    await bot.send_message(
        message.chat.id,
        ru.start_message,
        reply_markup=ru.start_keyboard
    )
    
@bot.callback_query_handler(lambda q: q.data == "start:setup")
async def start_setup(query: tg.CallbackQuery):
    await bot.edit_message_text(
        ru.start_setup_message,
        query.message.chat.id,
        query.message.id,
        reply_markup=ru.start_setup_keyboard
    )
    
    await bot.answer_callback_query(query.id)
    
@bot.callback_query_handler(lambda q: q.data == "start:setup:class" or q.data == "start:setup:teacher")
async def start_setup_select_type(query: tg.CallbackQuery):
    type = query.data.split(":")[2]
    message = (ru.start_setup_class_message if type == "class" else ru.start_setup_teacher_message)
    
    await bot.edit_message_text(
        message + ru.loading_data,
        query.message.chat.id,
        query.message.id,
        reply_markup=None
    )
    
    try:
        items = await (actions.get_classes() if type == "class" else actions.get_teachers())
        
        keyboard = tg.InlineKeyboardMarkup() \
            .add(*map(lambda a: tg.InlineKeyboardButton(a.name, callback_data=f"start:setup:{type}:{a.id}"), items), row_width=3) \
            .add(ru.start_setup_back_button)
        
        await bot.edit_message_text(
            message,
            query.message.chat.id,
            query.message.id,
            reply_markup=keyboard
        )
    except Exception as e:
        await error_reporter.report(e, traceback.format_exc())
        await bot.edit_message_text(
            ru.error_occured,
            query.message.chat.id,
            query.message.id,
            reply_markup=None
        )
        
    await bot.answer_callback_query(query.id)
      
@bot.callback_query_handler(lambda q: q.data.startswith("start:setup:teacher:") or q.data.startswith("start:setup:class:"))
async def start_setup_complete(query: tg.CallbackQuery):
    try:
        id = int(query.data.split(":")[-1])
    except: 
        return await bot.answer_callback_query(query.id, "Некорректный id")
    
    type = query.data.split(":")[2]
    
    already = list(filter(lambda a: a.receiver_id == query.message.chat.id and a.type == type and a.id == id, context.config.subscriptions))
    if len(already) == 0:
        context.config.subscriptions.append(Types.Subscription(receiver_id=query.message.chat.id, type=type, id=id))
        await context.save_config()
        
    choosed_item: str = "&lt;no data&gt;"
    for row in query.message.reply_markup.keyboard:
        for item in row:
            if item.callback_data == query.data:
                choosed_item = item.text
        
    await bot.edit_message_text(
        (ru.start_setup_class_complete if type == "class" else ru.start_setup_teacher_complete)(choosed_item),
        query.message.chat.id,
        query.message.id,
        reply_markup=None
    )
    
# НАСТРОЙКИ
@bot.message_handler(["settings", "start"])
async def settings(message: tg.Message):
    try:
        classes = await actions.get_classes()
        teachers = await actions.get_teachers()
        
        subscriptions = list(filter(lambda a: a.receiver_id == message.chat.id, context.config.subscriptions))
        
        await bot.send_message(
            message.chat.id,
            ru.settings(subscriptions, classes, teachers),
            reply_markup=ru.settings_keyboard
        )
    except Exception as e:
        await error_reporter.report(e, traceback.format_exc())
        await bot.send_message(
            message.chat.id,
            ru.error_occured,
            reply_markup=None
        )
        
@bot.callback_query_handler(lambda q: q.data == "settings")
async def settings(query: tg.CallbackQuery):
    try:
        classes = await actions.get_classes()
        teachers = await actions.get_teachers()
        
        subscriptions = list(filter(lambda a: a.receiver_id == query.message.chat.id, context.config.subscriptions))
        
        await bot.edit_message_text(
            ru.settings(subscriptions, classes, teachers),
            query.message.chat.id,
            query.message.id,
            reply_markup=ru.settings_keyboard
        )
    except Exception as e:
        await error_reporter.report(e, traceback.format_exc())
        await bot.edit_message_text(
            ru.error_occured,
            query.message.chat.id,
            query.message.id,
            reply_markup=None
        )
        
@bot.callback_query_handler(lambda q: q.data == "settings:add")
async def start_setup(query: tg.CallbackQuery):
    await bot.edit_message_text(
        ru.settings_add_message,
        query.message.chat.id,
        query.message.id,
        reply_markup=ru.settings_add_keyboard
    )
    
    await bot.answer_callback_query(query.id)

@bot.callback_query_handler(lambda q: q.data == "settings:add:class" or q.data == "settings:add:teacher")
async def start_setup_select_type(query: tg.CallbackQuery):
    type = query.data.split(":")[2]
    message = (ru.settings_add_class_message if type == "class" else ru.settings_add_teacher_message)
    
    await bot.edit_message_text(
        message + ru.loading_data,
        query.message.chat.id,
        query.message.id,
        reply_markup=None
    )
    
    try:
        items = await (actions.get_classes() if type == "class" else actions.get_teachers())
        
        keyboard = tg.InlineKeyboardMarkup() \
            .add(*map(lambda a: tg.InlineKeyboardButton(a.name, callback_data=f"settings:add:{type}:{a.id}"), items), row_width=3) \
            .add(ru.settings_add_back_button)
        
        await bot.edit_message_text(
            message,
            query.message.chat.id,
            query.message.id,
            reply_markup=keyboard
        )
    except Exception as e:
        await error_reporter.report(e, traceback.format_exc())
        await bot.edit_message_text(
            ru.error_occured,
            query.message.chat.id,
            query.message.id,
            reply_markup=None
        )
        
    await bot.answer_callback_query(query.id)
    
@bot.callback_query_handler(lambda q: q.data.startswith("settings:add:teacher:") or q.data.startswith("settings:add:class:"))
async def start_setup_complete(query: tg.CallbackQuery):
    try:
        id = int(query.data.split(":")[-1])
    except: 
        return await bot.answer_callback_query(query.id, "Некорректный id")
    
    type = query.data.split(":")[2]
    
    already = list(filter(lambda a: a.receiver_id == query.message.chat.id and a.type == type and a.id == id, context.config.subscriptions))
    if len(already) == 0:
        context.config.subscriptions.append(Types.Subscription(receiver_id=query.message.chat.id, type=type, id=id))
        await context.save_config()
        
    choosed_item: str = "&lt;no data&gt;"
    for row in query.message.reply_markup.keyboard:
        for item in row:
            if item.callback_data == query.data:
                choosed_item = item.text
        
    await bot.edit_message_text(
        (ru.settings_add_class_complete if type == "class" else ru.settings_add_teacher_complete)(choosed_item),
        query.message.chat.id,
        query.message.id,
        reply_markup=ru.return_to_settings_keyboard
    )
    
@bot.callback_query_handler(lambda q: q.data == "settings:manage")
async def settings_manage(query: tg.CallbackQuery):
    try:
        classes = await actions.get_classes()
        teachers = await actions.get_teachers()
        
        subscriptions = list(filter(lambda a: a.receiver_id == query.message.chat.id, context.config.subscriptions))
        
        keyboard = tg.InlineKeyboardMarkup()
        
        for sub in subscriptions:
            matched = list(filter(lambda a: a.id == sub.id, (classes if sub.type == "class" else teachers)))
            keyboard.add(tg.InlineKeyboardButton(("&lt;?&gt;" if len(matched) == 0 else f"{matched[0].name}"), callback_data=f"settings:manage:{sub.type}:{sub.id}"))
            
        keyboard.add(ru.return_to_settings_keyboard.keyboard[0][0])
        
        await bot.edit_message_text(
            ru.settings_manage_message,
            query.message.chat.id,
            query.message.id,
            reply_markup=keyboard
        )
    except Exception as e:
        await error_reporter.report(e, traceback.format_exc())
        await bot.edit_message_text(
            ru.error_occured,
            query.message.chat.id,
            query.message.id,
            reply_markup=None
        )
        
@bot.callback_query_handler(lambda q: q.data.startswith("settings:manage:") and len(q.data.split(":")) == 4)
async def settings_manage_selected(query: tg.CallbackQuery):
    type = query.data.split(":")[2]
    id = int(query.data.split(":")[-1])
    
    name = (await (actions.get_class(id) if type == "class" else actions.get_teacher(id)))[0].name
    
    await bot.edit_message_text(
        (ru.settings_manage_class if type == "class" else ru.settings_manage_teacher)(name),
        query.message.chat.id,
        query.message.id,
        reply_markup=ru.settings_manage_keyboard(type, id)
    )
    
@bot.callback_query_handler(lambda q: q.data.startswith("settings:manage:") and len(q.data.split(":")) == 5 and q.data.split(":")[-1] == "delete")
async def settings_delete(query: tg.CallbackQuery):
    type = query.data.split(":")[2]
    id = int(query.data.split(":")[3])
    
    context.config.subscriptions = list(filter(lambda a: not (a.receiver_id == query.message.chat.id and a.type == type and a.id == id), context.config.subscriptions))
    
    name = (await (actions.get_class(id) if type == "class" else actions.get_teacher(id)))[0].name
    
    await bot.edit_message_text(
        (ru.settings_manage_deleted_class_message if type == "class" else ru.settings_manage_deleted_teacher_message)(name),
        query.message.chat.id,
        query.message.id,
        reply_markup=ru.settings_manage_deleted_keyboard
    )