from __future__ import annotations
import asyncio

from get_replies.bilibili_api import get_timeline_replies, get_timeline_replies_by_bv, get_hot_replies, get_hot_replies_by_bv

class Reply:
    def __init__(self, **kwargs):
        self.member_id = kwargs['member_id']
        self.member_name = kwargs['member_name']
        self.comment = kwargs['comment']

    def __repr__(self):
        return 'Reply[member_uid={}, member_name={}, comment={}]'.format(self.member_uid, self.member_name, self.comment)


async def timeline_replies(av: int, *, pn_end: int, pn_start: int=1) -> list[Reply]:
    replies = []
    for pn in range(pn_start, pn_end + 1):
        reply_api_json = await get_timeline_replies(av, pn)
        data = reply_api_json['data']
        for single_json in data['replies']:
            replies.append(
                Reply(
                    member_id=single_json['member']['mid'],
                    member_name=single_json['member']['uname'],
                    comment=single_json['content']['message']
                )
            )
    await asyncio.sleep(.1)

    return replies


async def timeline_replies_by_bv(bv: str, *, pn_end: int, pn_start: int=1) -> list[Reply]:
    replies = []
    for pn in range(pn_start, pn_end + 1):
        reply_api_json = await get_timeline_replies_by_bv(bv, pn)
        data = reply_api_json['data']
        for single_json in data['replies']:
            replies.append(
                Reply(
                    member_id=single_json['member']['mid'],
                    member_name=single_json['member']['uname'],
                    comment=single_json['content']['message']
                )
            )
    await asyncio.sleep(.1)

    return replies


async def hot_replies(av: int, *, pn_end: int, pn_start: int=1) -> list[Reply]:
    replies = []
    for pn in range(pn_start, pn_end + 1):
        reply_api_json = await get_hot_replies(av, pn)
        data = reply_api_json['data']
        for single_json in data['replies']:
            replies.append(
                Reply(
                    member_id=single_json['member']['mid'],
                    member_name=single_json['member']['uname'],
                    comment=single_json['content']['message']
                )
            )
    await asyncio.sleep(.1)

    return replies


async def hot_replies_by_bv(bv: str, *, pn_end: int, pn_start: int=1) -> list[Reply]:
    replies = []
    for pn in range(pn_start, pn_end + 1):
        reply_api_json = await get_hot_replies_by_bv(bv, pn)
        data = reply_api_json['data']
        for single_json in data['replies']:
            replies.append(
                Reply(
                    member_id=single_json['member']['mid'],
                    member_name=single_json['member']['uname'],
                    comment=single_json['content']['message']
                )
            )
    await asyncio.sleep(.1)

    return replies
