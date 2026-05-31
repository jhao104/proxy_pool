# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     zdaye.py
   Description :   站大爷代理源
   Author :        JHao
   date：          2026/5/31
-------------------------------------------------
   Change Activity:
                   2026/05/31:
-------------------------------------------------
"""
__author__ = 'JHao'

from time import sleep
from datetime import datetime

from fetcher.baseFetcher import BaseFetcher
from util.webRequest import WebRequest


class ZdayeFetcher(BaseFetcher):
    """站大爷 https://www.zdaye.com/dayProxy.html"""

    name = "zdaye"
    url = "https://www.zdaye.com/dayProxy.html"

    def fetch(self):
        start_url = "https://www.zdaye.com/free/"
        html_tree = WebRequest().get(start_url, verify=False).tree
        latest_page_time = html_tree.xpath(
            "//span[@class='thread_time_info']/text()")[0].strip()
        interval = datetime.now() - datetime.strptime(
            latest_page_time, "%Y/%m/%d %H:%M:%S")
        if interval.seconds < 300:
            target_url = ("https://www.zdaye.com/"
                          + html_tree.xpath("//h3[@class='thread_title']/a/@href")[0].strip())
            while target_url:
                _tree = WebRequest().get(target_url, verify=False).tree
                for tr in _tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    yield "%s:%s" % (ip, port)
                next_page = _tree.xpath(
                    "//div[@class='page']/a[@title='下一页']/@href")
                target_url = ("https://www.zdaye.com/" + next_page[0].strip()
                              if next_page else False)
                sleep(5)


if __name__ == '__main__':
    for proxy in ZdayeFetcher().fetch():
        print(proxy)
