import asyncio
import datetime
import sys

from app import process_all_fields
from app import process_all_names
from app import fill_event_table_with_interval
from app import delete_events


async def fill_users() -> None:
    task_1 = asyncio.create_task(process_all_fields())
    task_2 = asyncio.create_task(process_all_names())
    await task_2
    await task_1


async def fill_events(option: str = "") -> None:
    now = datetime.datetime.today()
    delta = datetime.timedelta(days=now.weekday())
    new_delta = datetime.timedelta(days=21)
    fst_date = now - delta
    snd_date = fst_date + new_delta
    if option == "--delete":
        await delete_events(fst_date, snd_date)
    await fill_event_table_with_interval(fst_date, snd_date)
    # await fill_event_table_with_interval(datetime.datetime.strptime("2023-06-05", "%Y-%m-%d"),
    #                                      datetime.datetime.strptime("2023-07-05", "%Y-%m-%d"))


if __name__ == '__main__':
    if sys.argv[1] == "users":
        asyncio.run(fill_users())
    # sys.argv[1] == "events"
    else:
        if len(sys.argv) == 2:
            asyncio.run(fill_events())
        else:
            asyncio.run(fill_events(sys.argv[2]))
