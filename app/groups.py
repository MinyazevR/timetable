import aiohttp
import bs4
import typing as tp

from bs4 import PageElement, Tag, NavigableString
from sqlalchemy import text
from app import engine, execute_insert, get_html


async def fill_study_field_table(session, field_id: int, name: str, year: int):
    """Function for filling in the Field table"""

    await execute_insert(
        session,
        text('INSERT INTO "Field"(id, name, year)'
             'VALUES(:field_id, :name, :year)'
             'ON CONFLICT (id) DO NOTHING'), {
                 'field_id': field_id,
                 'name': name,
                 'year': year
             })


async def fill_group_table(session, group_id: int, name: str,
                           type_of_study: str, field_id: int):
    """Function for filling in the GroupOfStudy table"""

    await execute_insert(
        session,
        text('INSERT INTO "Group"(id, name, type, field_id) '
             'VALUES(:group_id, :name, :type_of_study, :field_id) '
             'ON CONFLICT (id) DO NOTHING'), {
                 'group_id': group_id,
                 'name': name,
                 'type_of_study': type_of_study,
                 'field_id': field_id
             })


def process_group(
        group: PageElement | Tag | NavigableString) -> tuple[tp.Any, ...]:
    """A function for processing information about each group"""

    group_link = group.get('onclick')
    try:
        group_id = int(group_link[group_link.rfind('/') + 1:-1])
    except ValueError:
        # logger
        raise

    if (col_sm_4 := group.find('div', attrs={'class':
                                             'col-sm-4'})) is not None:
        group_name = col_sm_4.text.strip()
    else:
        group_name = ""

    if (col_sm_3 := group.find('div', attrs={'class':
                                             'col-sm-3'})) is not None:
        group_type = col_sm_3.text.strip()
    else:
        group_type = ""

    return group_id, group_name, group_type


async def process_all_fields():
    """Function for processing all directions and groups"""
    host = "https://timetable.spbu.ru"
    async with aiohttp.ClientSession() as session:
        html = await get_html(host, session)
        parsed_html = bs4.BeautifulSoup(markup=html, features="lxml")
        col_of_faculty = parsed_html.findChild('div',
                                               attrs={'class': 'col-sm-6'})

        async with engine.connect() as bd_session:
            for faculty in col_of_faculty.findAll(
                    'li', attrs={'class': 'list-group-item'}):
                faculty_tag = faculty.find('a')
                faculty_link = faculty_tag.get('href')
                # name = direction.text

                faculty_html = bs4.BeautifulSoup(markup=(await get_html(
                    host + faculty_link, session)),
                                                 features="lxml")
                for panel_of_fields in faculty_html.findAll(
                        'div', attrs={'class': 'panel panel-default'}):
                    for field in panel_of_fields.findAll(
                            'li', attrs={'class': 'common-list-item row'}):
                        if (col_for_field_title
                                := field.find('div',
                                              attrs={'class':
                                                     'col-sm-5'})) is not None:
                            field_title = col_for_field_title.text.strip()
                        else:
                            continue
                        # Отбрасываем ненужные класссы
                        if (tags_a := field.findAll('a')) is None:
                            continue

                        # Ведем поиск по тегу
                        for tag_a in tags_a:
                            fields_link = tag_a.get('href')
                            try:
                                field_id = int(
                                    fields_link[fields_link.rfind('/') + 1:])
                                year = int(tag_a.text.strip())
                            except ValueError:
                                # logger
                                raise

                            # Заполняем таблицу для направления
                            await fill_study_field_table(
                                bd_session, field_id, field_title, year)
                            group_html = bs4.BeautifulSoup(
                                markup=(await get_html(host + fields_link,
                                                       session)),
                                features="lxml")

                            # Вырезаем расписания для предыдущих годов
                            for div in group_html.findAll(
                                    'ul', {'id': 'studentGroupsForPreviousYear'}):
                                div.decompose()

                            for group in group_html.findChildren(
                                    'div', attrs={'class': 'tile'}):
                                group_id, group_name, group_type = process_group(
                                    group)
                                await fill_group_table(bd_session, group_id,
                                                       group_name, group_type,
                                                       field_id)
