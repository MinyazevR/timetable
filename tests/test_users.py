import bs4
import aiofiles
import pytest


from test_common_csv import USER_INFO
from app import process_user


async def gen_for_users():
    async with aiofiles.open('tests/html_files/Users_A.html') as f:
        text = await f.read()
    parsed_html = bs4.BeautifulSoup(markup=text, features="lxml")
    rows = parsed_html.findAll('div', attrs={'class': 'tile'})
    for row in rows:
        yield row


@pytest.mark.asyncio
@pytest.mark.parametrize("user_values", USER_INFO)
async def test_get_user_info_by_bs4_element(user_values: tuple) -> None:
    number_of_elem = len(USER_INFO)
    counter = 0
    list_of_users = []

    async for row in gen_for_users():
        list_of_users.append(row)
        counter += 1
        if counter == number_of_elem:
            break

    list_of_users_info = [process_user(x) for x in list_of_users]

    assert USER_INFO == list_of_users_info
