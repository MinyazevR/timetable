import asyncio
import datetime
import aiohttp.web_exceptions
import asyncpg
import bs4

from sqlalchemy import text
from bs4 import element
from app import engine, execute_insert, get_html

__all__ = ['fill_event_table_with_interval', 'delete_events']


async def delete_events(session, left_date: datetime.datetime,
                        right_date: datetime.datetime) -> None:
    await session.execute(
        text('DELETE From "Event" '
             'WHERE "Event".start_time >= (:left_date) '
             'AND "Event".end_time <= (:right_date)'), {
            'left_date': left_date,
            'right_date': right_date
        })
    await session.commit()


async def fill_event_table(session, dt_start: datetime.datetime,
                           dt_end: datetime.datetime, subject: str,
                           location: str) -> int:
    """Function for filling in the Event table"""
    for i in range(2):
        result = await execute_insert(
            session,
            text(
                'WITH "ids" AS ('
                'INSERT INTO "Event" (start_time, end_time, description, location)'
                'VALUES(:start_time, :end_time, :description, :location)'
                'ON CONFLICT (start_time, end_time, description, location) '
                'DO NOTHING '
                'RETURNING id'
                ') SELECT COALESCE ('
                '(SELECT id FROM "ids"), '
                '(SELECT id FROM "Event" '
                'Where start_time=(:start_time) and end_time=(:end_time) '
                'and description=(:description) and location=(:location)));'),
            {
                'start_time': dt_start,
                'end_time': dt_end,
                'description': subject,
                'location': location
            })
        if (row := result.fetchone()) is None or (current_id :=
        row[0]) is None:
            continue
        return current_id

    raise asyncpg.NoDataFoundError()


async def fill_user_to_event_table(session, user_id: int, event_id: int):
    """Function for filling in the UserToEvent table"""
    await execute_insert(
        session,
        text(
            'INSERT INTO "UserToEvent" (user_id, event_id) VALUES(:user_id, :event_id) '
            'ON CONFLICT (user_id, event_id) '
            'DO NOTHING'), {
            'user_id': user_id,
            'event_id': event_id
        })


async def fill_group_to_event_table(session, group_id: int, event_id: int):
    """Function for filling in the GroupToEvent table"""
    await execute_insert(
        session,
        text(
            'INSERT INTO "GroupToEvent"(group_id, event_id) VALUES(:group_id, :event_id) '
            'ON CONFLICT (group_id, event_id) '
            'DO NOTHING'), {
            'group_id': group_id,
            'event_id': event_id
        })


def process_timetable_element(
        elem: element.Tag | element.NavigableString | None) -> str:
    return "" if elem is None else elem.text.strip()


def time_handler(times: str, current_year: int,
                 header_date: datetime.datetime) -> tuple[str, str]:
    """Function for processing time in the format %H:%M-%H:%M"""

    # На tt может время не в формате 15:00-17:00, а 15:00(без времени окончания)
    # Тут выгоднее сразу брать срезы и копировать чем создавать memoryview и копировать данные в новый буфер
    if len(times) >= 5:
        fixed_dt_time = datetime.datetime(year=current_year,
                                          day=header_date.day,
                                          month=header_date.month)
        start_delta = datetime.timedelta(hours=int(times[0:2]),
                                         minutes=int(times[3:5]))
        start_time = fixed_dt_time + start_delta
        if len(times) >= 11:
            end_delta = datetime.timedelta(hours=0, minutes=0, seconds=0)
            try:
                end_delta = datetime.timedelta(hours=int(times[6:8]),
                                               minutes=int(times[9:]))
            except ValueError:
                # logger
                pass
            end_time = fixed_dt_time + end_delta
            return start_time.strftime('%Y%m%dT%H%M%SZ'), end_time.strftime(
                '%Y%m%dT%H%M%SZ')
        else:
            return start_time.strftime('%Y%m%dT%H%M%SZ'), ""
    return "", ""


async def event_crawler(html: str, user_id: int,
                        initial_date: datetime.datetime,
                        groups: dict[str, str]) -> None:
    """Function for searching for information and filling in tables"""
    dct = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12
    }

    # Для определения дат для дней недели пользуемся датой из url
    initial_year = initial_date.year
    initial_month = initial_date.month
    initial_day = initial_date.day

    # Если неделя --- переход с одного года на другой, то для дней после первого января надо прибавить год на единицу
    change_year = initial_month == 12 and initial_day >= 25

    parsed_html = bs4.BeautifulSoup(markup=html, features="lxml")
    # Делим по дням недели
    day_panel = parsed_html.findAll('h4', attrs={'class': 'panel-title'})

    async with engine.connect() as session:
        # Каждому дню недели сопоставляем список пар
        for day in day_panel:

            # День недели и месяц в формате %day_of_week, %day %mont
            date_name = day.text.strip()

            # Имя дня недели не  интересует
            _, day_dt, month_name = date_name.split(' ')

            # В заголовке get запроса указано "Accept-Language": "ru-Ru", потому что иначе половина информации с tt
            # не будет выгружаться, не смотря на то что локаль --- 'en_US'.
            # чтобы не менять настройки локали, использую небольшой словарик
            header_date = datetime.datetime(day=int(day_dt),
                                            month=dct[month_name],
                                            year=initial_year)
            current_year = initial_year

            # Если текущий месяц январь, и неделя начиналась в декабря, то надо прибавить год
            if header_date.month == 1 and change_year:
                current_year += 1

            panel_for_the_day = day.findNext(
                "ul", attrs={'class': 'panel-collapse nopadding nomargin'})

            # Удаляем из дерева элементы, которые будут мешать при поиске(скрытая панель, дублирующая информацию)
            # for div in panel_for_the_day.findAll('div', attrs={'class': 'studyevent-location-educator-modal hidden'}):
            #     div.extract()

            # # Удаляем из дерева элементы, которые будут соответсвовать отмененным занятиям
            # for div in panel_for_the_day.findAll("span", {
            #     'class': ("hoverable moreinfo cancelled", "moreinfo cancelled", "hoverable link cancelled")}):
            #     div.decompose()

            for event in panel_for_the_day.findAll(
                    'li', attrs={'class': 'common-list-item row'}):

                # Обработка времени
                time_element = event.find(
                    'div', attrs={'class': "col-sm-2 studyevent-datetime"})

                # Смотрим отменено событие или нет
                cancelled = time_element.find(
                    'span', attrs={'class': "moreinfo cancelled"})

                # Если отменено, то не учитываем
                if cancelled is not None:
                    continue

                # Получаем время
                times = process_timetable_element(time_element)

                # Получаем левую и нижнюю границу времени
                start_time, end_time = time_handler(times, current_year,
                                                    header_date)

                # Обработка Дисциплины
                subject_element = event.find(
                    'div', attrs={'class': "col-sm-4 studyevent-subject"})

                # Пока что обрезал до 256, но может быть длинее
                subject_element = subject_element.find(
                    'span', attrs={'class': 'moreinfo'})
                subject = process_timetable_element(subject_element)[:256]

                # ('col-sm-3 studyevent-locations', 'col-sm-3 studyevent-multiple-locations')

                # Обработка места и группы
                location_and_groups_element = event.findAll(
                    'div', attrs={'class': 'col-sm-3'})

                location = "" if len(location_and_groups_element
                                     ) == 0 else process_timetable_element(
                    location_and_groups_element[0])

                if len(location) > 0 and location[-1] == "►":
                    location = location[:-1].strip()
                if (index := location.find(';')) != -1:
                    location = location[:index]

                groups_name = "" if len(location_and_groups_element
                                        ) < 2 else process_timetable_element(
                    location_and_groups_element[1])

                # Ксли время не указано, то в качестве значения по умолчанию берется начало unix-time
                dt_start = datetime.datetime(
                    year=1970, day=1, month=1
                ) if start_time == "" else datetime.datetime.strptime(
                    start_time, '%Y%m%dT%H%M%SZ')
                dt_end = datetime.datetime(
                    year=1970, day=1,
                    month=1) if end_time == "" else datetime.datetime.strptime(
                    end_time, '%Y%m%dT%H%M%SZ')

                # Заполняем таблицу Event
                event_id = await fill_event_table(session, dt_start, dt_end,
                                                  subject, location)

                # Заполянем таблицу UserToEvent
                await fill_user_to_event_table(session, user_id, event_id)

                # Обработка групп
                for group in groups_name.strip('''" ''').split(', '):
                    if group == "":
                        continue

                    # Находим id группы по названию, так как при выкачивании расписания нет ссылок на группы
                    if group in groups:
                        group_id = groups[group]
                    else:
                        continue

                    # Заполняем таблицу GroupToEvent
                    await fill_group_to_event_table(session, int(group_id),
                                                    event_id)


async def generate_week_url(session: aiohttp.ClientSession, user_id: int,
                            date_list, left_date: datetime.datetime,
                            groups: dict[str, str]):
    """A function to generate urls for each week and get their html"""

    task_list = []

    for x in date_list:
        task_list.append(
            asyncio.create_task(
                get_html(
                    f"https://timetable.spbu.ru/WeekEducatorEvents/{user_id}/{x}",
                    session)))

    for future in asyncio.as_completed(task_list):
        try:
            html = await future
        except aiohttp.web_exceptions.HTTPError:
            # logger
            raise
        await event_crawler(html, user_id, left_date, groups)


async def fill_event_table_with_interval(
        left_border: datetime.datetime,
        right_border: datetime.datetime) -> None:
    """Function for filling the Event table with events from a certain interval"""

    # Необходимо получить список групп
    # Сами события будет получать именно из раписания каждого пользователя
    async with engine.connect() as session:
        # удаляем события, начинающиеся с текущей недели
        await delete_events(session, left_border, right_border)
        groups = {
            x: y
            for x, y in (await session.execute(text('SELECT name, id FROM "Group"')
                                               )).fetchall()
        }
        user_row = (await
                    session.execute(text('SELECT id FROM "User"'))).fetchall()

    date_list = []
    delta = datetime.timedelta(days=7)
    copy_left_date = left_border

    while copy_left_date <= right_border:
        url_part = datetime.datetime.strftime(copy_left_date, "%Y-%m-%d")
        date_list.append(url_part)
        copy_left_date += delta

    lst = []
    async with aiohttp.ClientSession() as session:
        for elem in user_row:
            lst.append(
                asyncio.create_task(
                    generate_week_url(session, elem[0], date_list, left_border,
                                      groups)))
            if len(lst) == 200:
                await asyncio.gather(*lst)
                lst.clear()

        if len(lst) > 0:
            await asyncio.gather(*lst)
