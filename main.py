import asyncio
import datetime
import sys
from app import process_all_fields
from app import process_all_names
from app import fill_event_table_with_interval


async def fill_users() -> None:
    task_1 = asyncio.create_task(process_all_fields())
    task_2 = asyncio.create_task(process_all_names())
    await task_2
    await task_1


async def fill_events() -> None:
    now = datetime.datetime.today()
    delta = datetime.timedelta(days=now.weekday())
    fst_date = now - delta
    snd_date = fst_date + datetime.timedelta(days=28)
    await fill_event_table_with_interval(fst_date, snd_date)

if __name__ == '__main__':
    if sys.argv[1] == "users":
        asyncio.run(fill_users())
    # sys.argv[1] == "events"
    elif sys.argv[1] == "events":
        asyncio.run(fill_events())
