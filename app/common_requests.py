import aiohttp
import asyncio
import typing as tp
import asyncpg

from sqlalchemy.ext.asyncio import AsyncConnection


async def get_html(url: str, session: aiohttp.ClientSession) -> str:
    delay = 1
    for i in range(4):
        async with session.get(url=url,
                               headers={"Accept-Language":
                                        "ru-RU,ru;q=0.5"}) as resp:
            if resp.ok:
                return await resp.text()
            await asyncio.sleep(delay)
            delay *= 2
    async with session.get(url=url,
                           headers={"Accept-Language":
                                    "ru-RU,ru;q=0.5"}) as resp:
        if resp.ok:
            return await resp.text()
    resp.raise_for_status()
    return ""


async def execute_insert(session: AsyncConnection, txt,
                         dct: dict[str, tp.Any]):
    try:
        result = await session.execute(txt, dct)
    except asyncpg.IntegrityConstraintViolationError:
        # logger
        raise
    else:
        await session.commit()
    return result
