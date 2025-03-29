import asyncio
from rich.console import Console
from telebot import asyncio_helper
from typing import List

import actions
import const
import context
import datetime
import Types

c = Console()

async def report_class_subscribers(class_id: int, message: str):
    subs = map(lambda a: a.receiver_id, filter(lambda a: a.type == "class" and a.id == class_id, context.config.subscriptions))
    
    splitted = message.split("\n")
    n = 0
    messages = []
    now = []
    
    for part in splitted:
        if n + len(part) + 1 <= 4096:
            n += len(part) + 1
            now.append(part)
        else:
            messages.append("\n".join(now))
            now = [part]
            n = len(part) + 1
            
    if n > 0: messages.append("\n".join(now))
    
    async def send(sub: int):
        for message in messages:
            while True:
                try:
                    await context.bot.send_message(
                        sub,
                        message
                    )
                    break
                except asyncio_helper.ApiTelegramException as e:
                    if e.error_code == 429:
                        print(f'waiting {e.result_json['parameters']['retry_after']}')
                        await asyncio.sleep(e.result_json['parameters']['retry_after'])
                    else: 
                        c.print_exception(show_locals=True)
                        break
            
    for sub in subs:
        context.loop.create_task(send(sub))

async def update_schedule(info: Types.ScheduleUpdateInfo):
    tracked_classes = set(map(lambda a: a.id, filter(lambda a: a.type == "class", context.config.subscriptions)))
    
    b_classes = list(set(map(lambda a: a.class_id, info.before)))
    b_by_classes = {}
    
    for cl in b_classes:
        filtered = list(filter(lambda a: a.class_id == cl, info.before))
        periods = list(set(map(lambda a: a.period, filtered)))
        periods.sort()
        by_periods = {}
        
        for global_period in periods:
            by_periods[global_period] = list(filter(lambda a: a.period == global_period, filtered))
            
        b_by_classes[cl] = by_periods
        
    
    n_classes = list(set(map(lambda a: a.class_id, info.now)))
    n_by_classes = {}
    
    for cl in n_classes:
        filtered = list(filter(lambda a: a.class_id == cl, info.now))
        periods = list(set(map(lambda a: a.period, filtered)))
        periods.sort()
        by_periods = {}
        
        for global_period in periods:
            by_periods[global_period] = list(filter(lambda a: a.period == global_period, filtered))
            
        n_by_classes[cl] = by_periods
        
    classes = await actions.get_classes()
    teachers = await actions.get_teachers()
    subjects = await actions.get_subjects()
    classrooms = await actions.get_classrooms()
    periods = await actions.get_periods()
    blocks = await actions.get_blocks()
    
    def find(src: Types.OptionCollection, id: int):
        name = "&lt;no data&gt;"
        
        for opt in src:
            if opt.id == id: name = opt.name; break
            
        return name
    
    global_period = list(filter(lambda a: a.id == int(info.period), periods))[0]
    
    for cl in tracked_classes:
        class_obj = list(filter(lambda a: a.id == cl, classes))[0]
        if cl in b_classes and cl in n_classes:
            b = b_by_classes[cl]
            n = n_by_classes[cl]
            
            text = \
                f"<b>Изменено обычное расписание для класса {class_obj.name}</b>\n\n" + \
                f"<b>Период:</b> {global_period.name} ({global_period.start_time.strftime("%d.%m.%Y")} - {global_period.end_time.strftime("%d.%m.%Y")})\n" + \
                f"<b>День:</b> {const.WEEKDAYS[int(info.day)]}\n"
                
            needs_to_send = False
            
            for period in b:
                period_text = f"\n<b># {period} урок:</b>"
                needs_to_add = False
                
                if period not in n:
                    period_text += "\n<b>Удалены занятия:</b>"
                        
                    if b[period][0].block_id is not None:
                        period_text += f"\n<b>Блок:</b> {find(blocks, b[period][0].block_id)}"
                    
                    for entry in b[period]:
                        period_text += f"\n<b>- {find(subjects, entry.subject_id)}</b> ({find(teachers, entry.teacher_id)}, {find(classrooms, entry.classroom_id)})"
                        
                    period_text += \
                        "\n\n<b>Теперь:</b>" + \
                        "\n&lt;нет занятий&gt;\n"
                        
                    needs_to_add = True
                else:
                    bb: List[Types.ScheduleUpdateEntry] = b[period]
                    nn: List[Types.ScheduleUpdateEntry] = n[period]
                    
                    exclude: List[Types.ScheduleUpdateEntry] = []
                    
                    for lesson in bb:
                        found = len(list(filter(lambda a: lesson.block_id == a.block_id and lesson.block_part_id == a.block_part_id and lesson.class_id == a.class_id and lesson.classroom_id == a.classroom_id and lesson.subject_id == a.subject_id and lesson.teacher_id == a.teacher_id, nn))) > 0
                        if found: continue # мы нашли точно такой же урок => изменений нет => скипаем
                        needs_to_add = True
                        
                        if lesson.block_id is not None:
                            with_same_blockpart_id = list(filter(lambda a: lesson.block_part_id == a.block_part_id and lesson.block_id == a.block_id, nn))
                            if len(with_same_blockpart_id) > 0:
                                with_same_blockpart_id: Types.ScheduleUpdateEntry = with_same_blockpart_id[0]
                                period_text += \
                                    "\n<b>Заменено занятие в блоке:</b>" + \
                                    f"\n<b>Блок:</b> {find(blocks, lesson.block_id)}" + \
                                    f"\n<b>Предмет:</b> {find(subjects, with_same_blockpart_id.subject_id)}" + (f" (вместо {find(subjects, lesson.subject_id)})" if lesson.subject_id != with_same_blockpart_id.subject_id else "") + \
                                    f"\n<b>Учитель:</b> {find(teachers, with_same_blockpart_id.teacher_id)}" + (f" (вместо {find(teachers, lesson.teacher_id)})" if lesson.teacher_id != with_same_blockpart_id.teacher_id else "") + \
                                    f"\n<b>Кабинет:</b> {find(classrooms, with_same_blockpart_id.classroom_id)}" + (f" (вместо {find(classrooms, lesson.classroom_id)})" if lesson.classroom_id != with_same_blockpart_id.classroom_id else "") + "\n"
                            else:
                                period_text += \
                                    "\n<b>Удалено занятие из блока:</b>" + \
                                    f"\n<b>Блок:</b> {find(blocks, lesson.block_id)}" + \
                                    f"\n<b>Предмет:</b> {find(subjects, with_same_blockpart_id.subject_id)}" \
                                    f"\n<b>Учитель:</b> {find(teachers, with_same_blockpart_id.teacher_id)}" \
                                    f"\n<b>Кабинет:</b> {find(classrooms, with_same_blockpart_id.classroom_id)}\n"
                        else:
                            same_subject_before = list(filter(lambda a: lesson.subject_id == a.subject_id, bb))
                            same_subject_now = list(filter(lambda a: lesson.subject_id == a.subject_id, nn))
                            if len(same_subject_before) != 1 or len(same_subject_now) != 1:
                                same_teacher_before = list(filter(lambda a: lesson.teacher_id == a.teacher_id, same_subject_before))
                                same_teacher_now = list(filter(lambda a: lesson.teacher_id == a.teacher_id, same_subject_now))
                                
                                if len(same_teacher_before) != 1 or len(same_teacher_now) != 1:
                                    period_text += \
                                        "\n<b>Удалено занятие:</b>" + \
                                        f"\n<b>Предмет:</b> {find(subjects, lesson.subject_id)}" \
                                        f"\n<b>Учитель:</b> {find(teachers, lesson.teacher_id)}" \
                                        f"\n<b>Кабинет:</b> {find(classrooms, lesson.classroom_id)}\n"
                                else:
                                    same_teacher = same_teacher_now[0]
                                    exclude.append(same_teacher)
                                    period_text += \
                                        f"\n<b>Заменен кабинет</b>" + \
                                        f"\n<b>Предмет:</b> {find(subjects, same_subject.subject_id)}" + \
                                        f"\n<b>Учитель:</b> {find(teachers, same_subject.teacher_id)}" + \
                                        f"\n<b>Кабинет:</b> {find(classrooms, same_subject.classroom_id)}" + (f" (вместо {find(classrooms, lesson.classroom_id)})" if lesson.classroom_id != same_subject.classroom_id else "") + "\n"
                            else:
                                same_subject = same_subject_now[0]
                                exclude.append(same_subject)
                                period_text += \
                                    f"\n<b>{"Заменены учитель и кабинет" if lesson.teacher_id != same_subject.teacher_id and lesson.classroom_id != same_subject.classroom_id else "Заменен учитель" if lesson.teacher_id != same_subject.teacher_id else "Заменен кабинет" if lesson.classroom_id != same_subject.classroom_id else f"Заменены какие-то данные в занятии (я не понял, какие именно, это сообщение вообще не должно появляться, но раз ты его видишь, перешли его @levonciy; <a href=\"https://levonciy.ru/?before={lesson.model_dump_json()}&now={same_subject.model_dump_json()}\">тех. данные</a>)"}</b>" + \
                                    f"\n<b>Предмет:</b> {find(subjects, same_subject.subject_id)}" + \
                                    f"\n<b>Учитель:</b> {find(teachers, same_subject.teacher_id)}" + (f" (вместо {find(teachers, lesson.teacher_id)})" if lesson.teacher_id != same_subject.teacher_id else "") + \
                                    f"\n<b>Кабинет:</b> {find(classrooms, same_subject.classroom_id)}" + (f" (вместо {find(classrooms, lesson.classroom_id)})" if lesson.classroom_id != same_subject.classroom_id else "") + "\n"
                                    
                    for lesson in nn:
                        found = len(list(filter(lambda a: lesson.block_id == a.block_id and lesson.block_part_id == a.block_part_id and lesson.class_id == a.class_id and lesson.classroom_id == a.classroom_id and lesson.subject_id == a.subject_id and lesson.teacher_id == a.teacher_id, bb + exclude))) > 0
                        if found: continue # мы нашли точно такой же урок => изменений нет => скипаем
                        needs_to_add = True
                        
                        if lesson.block_id is not None:
                            with_same_blockpart_id = list(filter(lambda a: lesson.block_part_id == a.block_part_id and lesson.block_id == a.block_id, bb))
                            if len(with_same_blockpart_id) == 0:
                                period_text += \
                                    "\n<b>Добавлено занятие в блок:</b>" + \
                                    f"\n<b>Блок:</b> {find(blocks, lesson.block_id)}" + \
                                    f"\n<b>Предмет:</b> {find(subjects, with_same_blockpart_id.subject_id)}" \
                                    f"\n<b>Учитель:</b> {find(teachers, with_same_blockpart_id.teacher_id)}" \
                                    f"\n<b>Кабинет:</b> {find(classrooms, with_same_blockpart_id.classroom_id)}\n"
                        else:
                            period_text += \
                                "\n<b>Добавлено занятие:</b>" + \
                                f"\n<b>Предмет:</b> {find(subjects, lesson.subject_id)}" \
                                f"\n<b>Учитель:</b> {find(teachers, lesson.teacher_id)}" \
                                f"\n<b>Кабинет:</b> {find(classrooms, lesson.classroom_id)}\n"
                                
                    
                    period_text += \
                        "\n<b>Теперь:</b>"
                        
                    for entry in n[period]:
                        period_text += f"\n<b>- {find(subjects, entry.subject_id)}</b> ({find(teachers, entry.teacher_id)}, {find(classrooms, entry.classroom_id)})"
                        
                    period_text += "\n"
                        
                if needs_to_add:
                    text += period_text + "\n"
                    needs_to_send = True
            for period in n:
                if period not in b:
                    text += \
                        f"\n<b># {period} урок:</b>\n<b>Добавлены занятия:</b>"
                        
                    if n[period][0].block_id is not None:
                        text += f"\n<b>Блок:</b> {find(blocks, n[period][0].block_id)}"
                        
                    for entry in n[period]:
                        text += f"\n<b>- {find(subjects, entry.subject_id)}</b> ({find(teachers, entry.teacher_id)}, {find(classrooms, entry.classroom_id)})"
                        
                    text += "\n"
                        
                    needs_to_send = True

            if needs_to_send: await report_class_subscribers(cl, text)
        elif cl in b_classes and cl not in n_classes:
            await report_class_subscribers(
                cl, 
                f"<b>Удалено обычное расписание для класса {class_obj.name}</b>\n\n"
                f"<b>Период:</b> {global_period.name} ({global_period.start_time.strftime("%d.%m.%Y")} - {global_period.end_time.strftime("%d.%m.%Y")})\n"
                f"<b>День:</b> {const.WEEKDAYS[int(info.day)]}\n\n"
            )
        elif cl not in b_classes and cl in n_classes:
            await report_class_subscribers(
                cl, 
                f"<b>Добавлено обычное расписание для класса {class_obj.name}</b>\n\n"
                f"<b>Период:</b> {global_period.name} ({global_period.start_time.strftime("%d.%m.%Y")} - {global_period.end_time.strftime("%d.%m.%Y")})\n"
                f"<b>День:</b> {const.WEEKDAYS[int(info.day)]}\n\n"
            )
            
