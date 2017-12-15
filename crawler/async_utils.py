import asyncio
import functools
import logging

import aiohttp


async def async_get(url, loop):
    async with aiohttp.ClientSession() as session:
        for i in range(1):
            r = await session.get(url)
            j = await r.json()
            loop.call_soon(functools.partial(logging.debug, '%s parse, done.' % url))
            return j


def async__loop_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()
