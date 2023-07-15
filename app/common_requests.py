import aiohttp
import asyncio

import typing as tp
import asyncpg
from sqlalchemy import TextClause, Result
from sqlalchemy.ext.asyncio import AsyncSession


async def get_html(url: str) -> str:
    delay = 1
    async with aiohttp.ClientSession() as session:
        for i in range(4):
            async with session.get(
                    url=url, headers={"Accept-Language":
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


async def execute_insert(session: AsyncSession, txt: TextClause,
                         dct: dict[str, tp.Any]) -> Result:
    try:
        result = await session.execute(txt, dct)
    except asyncpg.IntegrityConstraintViolationError:
        # logger
        raise
    else:
        await session.commit()
    return result
