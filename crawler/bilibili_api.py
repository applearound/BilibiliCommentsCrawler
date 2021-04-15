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


async def get_aid_from_bv(bv: str, session: aiohttp.ClientSession=None) -> int:
    html_content = await get_video_page_content(bv, session)
    soup = bs4.BeautifulSoup(html_content, 'html.parser')
    url_meta = soup.find('meta', attrs={'itemprop': 'url'})
    url = url_meta['content']
    parsed_url = urllib.parse.urlparse(url)
    aid = parsed_url.path.rstrip('/').split('/')[-1].lstrip('av')
    return int(aid)


async def get_hot_reply(bv: str, page: int=1, session: aiohttp.ClientSession=None):
    auto_close = False
    if session is None:
        session = aiohttp.ClientSession()
        auto_close = True
    
    try:
        aid = await get_aid_from_bv(bv, session)
    except Exception as e:
        await session.close()
        raise e

    query_params = {
        # 'callback': 'jQuery33103988324956513716_1618491819366',
        'jsonp': 'jsonp',
        'pn': page,
        'type': 1,
        'oid': aid,
        'sort': 2,
        '_': int(datetime.datetime.now().timestamp() * 1000)
    }

    try:
        async with session.get('https://api.bilibili.com/x/v2/reply', params=query_params) as response:
            json_data = await response.json()
    finally:
        if auto_close:
            await session.close()
    return json_data

loop = asyncio.get_event_loop()
r = loop.run_until_complete(get_hot_reply('1iy4y1x7vY'))

for comment in r['data']['replies']:
    print(comment['content']['message'])
