import argparse
import asyncio
import logging
import mmap
import os
import re
import sys

from get_replies.reply import timeline_replies, timeline_replies_by_bv, hot_replies, hot_replies_by_bv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    stream=sys.stdout
)

arg_parser = argparse.ArgumentParser()
av_or_bv_group = arg_parser.add_mutually_exclusive_group(required=True)
av_or_bv_group.add_argument(
    '--av',
    help='av number of a video',
    type=int
)
av_or_bv_group.add_argument(
    '--bv',
    help='bv number of a video',
    type=str
)
arg_parser.add_argument(
    '-o',
    '--output',
    help='path of the output file',
    type=str,
    default='replies.txt'
)
arg_parser.add_argument(
    '-s',
    '--sort',
    help='how to sort comments',
    type=str,
    choices=('hot', 'time'),
    default='time'
)
arg_parser.add_argument(
    '-n',
    '--page',
    help='max pages to get',
    type=int,
    default=1
)

args = arg_parser.parse_args()

av = args.av
bv = args.bv
output_file = args.output
sort = args.sort
pn = args.page


async def av_main(av: int, sort, pn):
    if sort == 'time':
        return await timeline_replies(av, pn_start=1, pn_end=1 + pn - 1)
    elif sort == 'hot':
        return await hot_replies(av, pn_start=1, pn_end=1 + pn - 1)
    else:
        raise Exception('incorrect sort value')


async def bv_main(bv: str, sort, pn):
    if sort == 'time':
        return await timeline_replies_by_bv(bv, pn_start=1, pn_end=1 + pn - 1)
    elif sort == 'hot':
        return await hot_replies_by_bv(bv, pn_start=1, pn_end=1 + pn - 1)
    else:
        raise Exception('incorrect sort value')


if __name__ == '__main__':
    if sys.platform == 'win32' and sys.version_info.minor < 8:
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()

    replies = None
    if av is not None:
        replies = loop.run_until_complete(av_main(av, sort, pn))
    elif bv is not None:
        replies = loop.run_until_complete(bv_main(bv, sort, pn))
    else:
        raise Exception('missing argument')

    try:
        block_size = 1 << 12

        fd = os.open(output_file, flags=os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        os.ftruncate(fd, block_size)
        mm_flie = mmap.mmap(fd, length=block_size, offset=0, access=mmap.ACCESS_WRITE)

        block_number = 1
        write_len = 0
        total_write = 0
        for reply in replies:
            record_bytes = '{} - {}\n{}\n'.format(reply.member_id, reply.member_name, reply.comment).encode('utf-8')
            record_len = len(record_bytes)
            if write_len + record_len > block_size:
                need_write = block_size - write_len
                
                mm_flie.write(record_bytes[:need_write])
                mm_flie.flush()
                mm_flie.close()
                os.ftruncate(fd, block_size * (block_number + 1))
                block_number += 1
                mm_flie = mmap.mmap(fd, length=block_size, offset=block_size * (block_number - 1), access=mmap.ACCESS_WRITE)
                mm_flie.write(record_bytes[need_write:])
                write_len = record_len - need_write
            else:
                mm_flie.write(record_bytes)
                write_len += record_len
            total_write += record_len
        mm_flie.flush()
        os.ftruncate(fd, total_write)
    finally:
        mm_flie.close()
        os.close(fd)
