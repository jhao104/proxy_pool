# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     check
   Description :   执行代理校验
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: 执行代理校验
                   2021/05/25: 分别校验http和https
                   2022/08/16: 获取代理Region信息
                   2026/09/05: 失败代理拉黑(伪造120分钟/网络失败60分钟), 池内连续失败满5分钟才作废
                   2026/11/14: 新代理验证通过时记录各源可用数量, 供采集统计使用
                   2026/11/14: 记录校验时间戳, 供校验速度统计使用
                   2026/11/14: 校验过程中周期性落库统计, 避免大批量验证时接口长时间为0
-------------------------------------------------
"""
__author__ = 'JHao'

from util.six import Empty
from threading import Thread, Event
from datetime import datetime
from util.webRequest import WebRequest
from handler.logHandler import LogHandler
from helper.validator import ProxyValidator
from helper.sourceStat import source_stat
from helper.speedStat import speed_stat
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler
from helper.blacklist import fail_blacklist, FAIL_EXPIRE_TIME

# 统计落库间隔(秒): 大批量验证时长时间才有整轮结束, 期间也要能查到数据
STAT_FLUSH_INTERVAL = 30


class DoValidator(object):
    """ 执行校验 """

    conf = ConfigHandler()

    @classmethod
    def validator(cls, proxy, work_type):
        """
        校验入口
        Args:
            proxy: Proxy Object
            work_type: raw/use
        Returns:
            Proxy Object
        """
        http_r = cls.httpValidator(proxy)
        https_r = False if http_r is not True else cls.httpsValidator(proxy)

        proxy.check_count += 1
        proxy.last_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        proxy.last_status = http_r is True
        if http_r is True:
            if proxy.fail_count > 0:
                proxy.fail_count -= 1
            proxy.https = True if https_r else False
            if work_type == "raw":
                proxy.region = cls.regionGetter(proxy) if cls.conf.proxyRegion else ""
        else:
            proxy.fail_count += 1
        # 伪造标记(瞬态属性, 不入库): 响应可达但内容不符, 供黑名单区分拉黑时长
        proxy.fake_flag = (http_r == "FAKE")
        return proxy

    @classmethod
    def httpValidator(cls, proxy):
        for func in ProxyValidator.http_validator:
            result = func(proxy.proxy)
            if result == "FAKE":
                return "FAKE"
            if not result:
                return False
        return True

    @classmethod
    def httpsValidator(cls, proxy):
        for func in ProxyValidator.https_validator:
            if not func(proxy.proxy):
                return False
        return True

    @classmethod
    def preValidator(cls, proxy):
        for func in ProxyValidator.pre_validator:
            if not func(proxy):
                return False
        return True

    @classmethod
    def regionGetter(cls, proxy):
        try:
            url = 'https://api.ip.sb/geoip/%s' % proxy.proxy.split(':')[0]
            r = WebRequest().get(url=url, retry_time=1, timeout=2).json
            return r.get('country_code')
        except:
            return 'error'


class _ThreadChecker(Thread):
    """ 多线程检测 """

    def __init__(self, work_type, target_queue, thread_name):
        Thread.__init__(self, name=thread_name)
        self.work_type = work_type
        self.log = LogHandler("checker")
        self.proxy_handler = ProxyHandler()
        self.target_queue = target_queue
        self.conf = ConfigHandler()

    def run(self):
        self.log.info("{}ProxyCheck - {}: start".format(self.work_type.title(), self.name))
        while True:
            try:
                proxy = self.target_queue.get(block=False)
            except Empty:
                self.log.info("{}ProxyCheck - {}: complete".format(self.work_type.title(), self.name))
                break
            proxy = DoValidator.validator(proxy, self.work_type)
            # 记录一次校验完成(无论结果), 供 1/5/10 分钟速度统计
            speed_stat.record()
            if self.work_type == "raw":
                self.__ifRaw(proxy)
            else:
                self.__ifUse(proxy)
            self.target_queue.task_done()

    def __ifRaw(self, proxy):
        if proxy.last_status:
            if self.proxy_handler.exists(proxy):
                self.log.info('RawProxyCheck - {}: {} exist'.format(self.name, proxy.proxy.ljust(23)))
            else:
                self.log.info('RawProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
                self.proxy_handler.put(proxy)
            # 抓取后验证通过即计入该来源的可用数量(已存在池中同样算可用)
            source_stat.recordValid(proxy)
        else:
            # 失败拉黑, 拉黑期内采集直接跳过: 伪造120分钟, 其他失败60分钟
            fail_blacklist.add(proxy.proxy, fake=getattr(proxy, "fake_flag", False))
            self.log.info('RawProxyCheck - {}: {} fail'.format(self.name, proxy.proxy.ljust(23)))

    def __ifUse(self, proxy):
        if proxy.last_status:
            fail_blacklist.clearFail(proxy.proxy)
            self.log.info('UseProxyCheck - {}: {} pass'.format(self.name, proxy.proxy.ljust(23)))
            self.proxy_handler.put(proxy)
        else:
            if getattr(proxy, "fake_flag", False):
                # 伪造代理一次即拉黑120分钟, 并直接移出代理池
                fail_blacklist.add(proxy.proxy, fake=True)
                self.log.info('UseProxyCheck - {}: {} fake, delete blacklist120'.format(self.name,
                                                                                       proxy.proxy.ljust(23)))
                self.proxy_handler.delete(proxy)
            elif fail_blacklist.markFail(proxy.proxy) >= FAIL_EXPIRE_TIME:
                # 网络型失败要连续满5分钟才作废, 避免网络波动一次误杀
                fail_blacklist.add(proxy.proxy)
                self.log.info('UseProxyCheck - {}: {} fail连续满5分钟, delete blacklist60'.format(self.name,
                                                                                                 proxy.proxy.ljust(23)))
                self.proxy_handler.delete(proxy)
            else:
                self.log.info('UseProxyCheck - {}: {} fail, count {} keep'.format(self.name,
                                                                                  proxy.proxy.ljust(23),
                                                                                  proxy.fail_count))
                self.proxy_handler.put(proxy)


class _StatFlusher(Thread):
    """校验期间周期性落库统计, 避免大批量验证时接口长时间读不到数据"""

    def __init__(self, stop_event, interval=STAT_FLUSH_INTERVAL):
        Thread.__init__(self, name="stat_flusher")
        self.stop_event = stop_event
        self.interval = interval
        self.log = LogHandler("checker")

    def run(self):
        while not self.stop_event.wait(self.interval):
            flushStats()

    def final(self):
        """校验结束后补一次, 确保最后一批数据入库"""
        flushStats()


def flushStats():
    """把当前采集/速度统计写入数据库"""
    try:
        handler = ProxyHandler()
        handler.saveSourceStat(source_stat.snapshot())
        handler.saveSpeedStat(speed_stat.dump())
    except Exception as e:
        LogHandler("checker").error("Stat flush error: %s" % str(e))


def Checker(tp, queue):
    """
    run Proxy ThreadChecker
    :param tp: raw/use
    :param queue: Proxy Queue
    :return:
    """
    thread_list = list()
    for index in range(20):
        thread_list.append(_ThreadChecker(tp, queue, "thread_%s" % str(index).zfill(2)))

    # 校验期间每 30 秒落库一次统计
    stop_event = Event()
    flusher = _StatFlusher(stop_event)
    flusher.setDaemon(True)
    flusher.start()

    try:
        for thread in thread_list:
            thread.setDaemon(True)
            thread.start()

        for thread in thread_list:
            thread.join()
    finally:
        stop_event.set()
        flusher.final()
