import argparse
import asyncio
import logging
import math
import os
import re
import sys
import threading
import time

import requests as r

from async_utils import async__loop_thread, async_get

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    stream=sys.stdout)

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    'av', help='av number of the video. "av23333 or 23333"')
arg_parser.add_argument(
    '-s', '--sort', help='sort method. [-128 - 127]', default='0')
arg_parser.add_argument(
    '-f',
    '--file',
    help='full path of the output file and its name.',
    default=os.path.abspath(
        os.path.join(
            os.path.join(os.path.dirname(__file__),
                         '..\\data\\comments.txt'))))
args = arg_parser.parse_args()

av = args.av
if not re.match('^((av)?)(\d+)$', av):
    logging.error('av number format error.')
    exit()
if av.startswith('av'):
    av = av[2:]

sort = args.sort
file_path = args.file

try:
    import uvloop
except ImportError:
    logging.info('Module "uvloop" dose not exists.')
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

url_template = 'https://api.bilibili.com/x/v2/reply?type=1&oid=%s&sort=%s&pn={pn}' % (
    av, sort)

url = url_template.format(pn='1')

page_info = r.get(url)
page_info_json = page_info.json()

comments_count = page_info_json['data']['page']['count']
comments_per_page = page_info_json['data']['page']['size']
total_pages = math.ceil(comments_count / comments_per_page)

if total_pages > 1:
    loop = asyncio.ProactorEventLoop(
    ) if sys.platform == 'win32' else asyncio.new_event_loop()

    t = threading.Thread(target=async__loop_thread, args=(loop, ))
    t.daemon = True
    t.start()

    futures = []

    for i in range(2, 1 + total_pages):
        if i % 100 == 0:
            time.sleep(2)
        futures.append(
            asyncio.run_coroutine_threadsafe(
                async_get(url_template.format(pn=i), loop), loop))

    results = []
    timeout_list = []
    for future in futures:
        try:
            results.append(future.result(1))
        except asyncio.TimeoutError:
            timeout_list.append(future)

    for future in timeout_list:
        try:
            results.append(future.result(3))
        except asyncio.TimeoutError:
            logging.error(future, 'timeout.')

    with open(file_path, 'wt', encoding='utf-8') as f:
        logging.info('file stored in %s.' % file_path)
        for result in results:
            for reply in result['data']['replies']:
                f.write('--%s:\n%s\n----------------------------------\n' %
                        (reply['rpid_str'], reply['content']['message']))
