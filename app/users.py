import asyncio
import bs4
import typing as tp

from bs4 import PageElement, Tag, NavigableString
from sqlalchemy import text
from app import engine, get_html, execute_insert


async def fill_user_table(user_id: int, first_name: str, last_name,
                          middle_name, post: str, department: str) -> None:
    """Function for filling in the User table"""

    async with engine.connect() as session:
        await execute_insert(
            session,
            text(
                'INSERT INTO "User" (id, first_name, last_name, middle_name, post, department) '
                'VALUES(:user_id, :first_name, :last_name, :middle_name, :post, :department)'
                'ON CONFLICT DO NOTHING;'), {
                    'user_id': user_id,
                    'first_name': first_name,
                    'last_name': last_name,
                    'middle_name': middle_name,
                    'post': post,
                    'department': department
                })


async def process_all_names(
        url: str = "https://timetable.spbu.ru/EducatorEvents/Index") -> None:
    """Function for processing all variants of surnames"""

    task_list = []
    for i in range(1040, 1072):
        task_list.append(
            asyncio.create_task(
                get_html(
                    f"https://timetable.spbu.ru/EducatorEvents/Index?q={chr(i)}"
                )))
    for future in asyncio.as_completed(task_list):
        await process_all_users(await future)


async def process_all_users(html: str) -> None:
    """A function for processing information about users"""

    parsed_html = bs4.BeautifulSoup(markup=html, features="lxml")
    rows = parsed_html.findAll('div', attrs={'class': 'tile'})

    if rows is None:
        return

    for row in rows:
        result = process_user(row)
        if result is None:
            continue
        # Получаем информацию о преподавателе
        user_id, first_name, last_name, middle_name, posts, departments = result

        # Заполнение таблицы преподаватель
        await fill_user_table(user_id, first_name, last_name, middle_name,
                              posts, departments)


def process_user(
        row: PageElement | Tag | NavigableString) -> None | tuple[tp.Any, ...]:
    """A function for processing information about each user"""

    try:
        # Ссылка на преподавателя
        user_link = row.get('onclick')

        # Id Преподавателя на tt
        user_id = int(user_link[user_link.rfind('/') + 1:-1])

        # Кафедра
        department_name_part = row.findNext('div', attrs={
            'class': 'col-sm-7'
        }).text.strip()

        # Имя
        name = row.findNext('div', attrs={'class': 'col-sm-3'}).text.strip()

        # Должность
        post = row.findNext('div', attrs={'class': 'col-sm-2'}).text.strip()
    except IndexError:
        # logger
        raise
    except ValueError:
        # logger
        raise
    except AttributeError:
        # logger
        raise

    # Кафедр может быть несколько(пока что просто в строку)
    department_name_parts = [
        x.strip() for x in department_name_part.split('\n')
    ]

    # Должностей может быть несколько(пока что просто в строку)
    posts = [x.strip() for x in post.split('\n')]

    full_name = name.split(' ')

    if len(full_name) < 2:
        return None

    first_name = full_name[0]
    last_name = full_name[1]
    middle_name: None | str = None

    if len(full_name) >= 3:
        middle_name = " ".join(full_name[2:])

    return user_id, first_name, last_name, middle_name, " ".join(
        posts), " ".join(department_name_parts)
