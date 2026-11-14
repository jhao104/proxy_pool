# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
                   2026/09/05: 采集跳过拉黑期内代理, 避免重复验活积压队列
                   2026/11/14: 每轮采集结束后保存各源采集统计
                   2026/11/14: 每轮校验后保存校验速度统计
-------------------------------------------------
"""
__author__ = 'JHao'

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from helper.sourceStat import source_stat
from helper.speedStat import speed_stat
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler
from helper.blacklist import fail_blacklist


def __runProxyFetch():
    proxy_queue = Queue()
    proxy_fetcher = Fetcher()

    # 统计按轮重置: 本轮抓取数/可用数只反映这一轮
    source_stat.reset()
    for proxy in proxy_fetcher.run():
        # 拉黑期内的代理直接跳过, 不再重复验活
        if fail_blacklist.isBlacklisted(proxy.proxy):
            continue
        proxy_queue.put(proxy)

    Checker("raw", proxy_queue)
    __saveSourceStat()
    __saveSpeedStat()


def __saveSourceStat():
    """把本轮采集统计落库, 供 server 进程的 /count/source 读取"""
    try:
        ProxyHandler().saveSourceStat(source_stat.snapshot())
    except Exception as e:
        LogHandler("scheduler").error("SourceStat save error: %s" % str(e))


def __saveSpeedStat():
    """把最近10分钟校验时间戳落库, 供 server 进程的 /count/speed 读取"""
    try:
        ProxyHandler().saveSpeedStat(speed_stat.dump())
    except Exception as e:
        LogHandler("scheduler").error("SpeedStat save error: %s" % str(e))


def __runProxyCheck():
    proxy_handler = ProxyHandler()
    proxy_queue = Queue()
    if proxy_handler.db.getCount().get("total", 0) < proxy_handler.conf.poolSizeMin:
        __runProxyFetch()
    for proxy in proxy_handler.getAll():
        proxy_queue.put(proxy)
    Checker("use", proxy_queue)
    __saveSpeedStat()


def runScheduler():
    __runProxyFetch()

    timezone = ConfigHandler().timezone
    scheduler_log = LogHandler("scheduler")
    scheduler = BlockingScheduler(logger=scheduler_log, timezone=timezone)

    scheduler.add_job(__runProxyFetch, 'interval', minutes=5, id="proxy_fetch", name="proxy采集")
    scheduler.add_job(__runProxyCheck, 'interval', minutes=2, id="proxy_check", name="proxy检查")
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }

    scheduler.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)

    scheduler.start()


if __name__ == '__main__':
    runScheduler()
