import asyncio
import datetime
import urllib

import aiohttp
import bs4

"""
Query Params:
callback = jQuery33103988324956513716_1618491819366
jsonp = jsonp
pn = 3
type = 1
oid = 887285744
sort = 2
_ = 1618491819371
"""
VIDEO_API = 'https://www.bilibili.com/video'
HOT_REPLY_API = 'https://api.bilibili.com/x/v2/reply'


async def get_video_page_content(bv: str, session: aiohttp.ClientSession=None) -> str:
    if session is None:
        async with aiohttp.ClientSession() as session:
            async with session.get(VIDEO_API + '/BV' + bv) as response:
                return await response.text()
    else:
        async with session.get(VIDEO_API + '/BV' + bv) as response:
            return await response.text()


async def bv_to_av(bv: str, session: aiohttp.ClientSession=None) -> int:
    html_content = await get_video_page_content(bv, session)
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    url_meta = soup.find('meta', attrs={'itemprop': 'url'})
    url = url_meta['content']
    parsed_url = urllib.parse.urlparse(url)
    av = parsed_url.path.rstrip('/').split('/')[-1].lstrip('av')
    return int(av)


async def get_hot_replies_by_bv(bv: str, page: int=1, session: aiohttp.ClientSession=None) -> dict:
    auto_close = False
    if session is None:
        session = aiohttp.ClientSession()
        auto_close = True
    
    av = await bv_to_av(bv, session)
    r = await get_hot_replies(av, page, session)

    if auto_close:
        await session.close()

    return r


async def get_timeline_replies_by_bv(bv: str, page: int=1, session: aiohttp.ClientSession=None) -> dict:
    auto_close = False
    if session is None:
        session = aiohttp.ClientSession()
        auto_close = True
    
    av = await bv_to_av(bv, session)
    r = await get_timeline_replies(av, page, session)

    if auto_close:
        await session.close()

    return r


async def get_hot_replies(av: int, page: int=1, session: aiohttp.ClientSession=None) -> dict:
    return await get_replies(
        av=av,
        page=page,
        type=1,
        sort=2,
        session=session
    )


async def get_timeline_replies(av: int, page: int=1, session: aiohttp.ClientSession=None) -> dict:
    return await get_replies(
        av=av,
        page=page,
        type=1,
        sort=0,
        session=session
    )


async def get_replies(
    av: int,
    page: int=1,
    type: int=1,
    sort: int=0,
    session: aiohttp.ClientSession=None
) -> dict:
    auto_close = False
    if session is None:
        session = aiohttp.ClientSession()
        auto_close = True

    # type 1 热度
    # sort 0 时间排序
    # sort 2 热度排序
    query_params = {
        # 'callback': 'jQuery33103988324956513716_1618491819366',
        # 'jsonp': 'jsonp',
        'pn': page,
        'type': type,
        'oid': av,
        'sort': sort,
        '_': int(datetime.datetime.now().timestamp() * 1000)
    }

    try:
        async with session.get('https://api.bilibili.com/x/v2/reply', params=query_params) as response:
            json_data = await response.json()
    finally:
        if auto_close:
            await session.close()
    return json_data
