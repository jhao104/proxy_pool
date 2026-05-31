# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     fetch.py
   Description :   代理采集
   Author :        JHao
   date：          2019/8/6
-------------------------------------------------
   Change Activity:
                   2019/08/06: 多线程采集
                   2026/05/31: 重构为动态加载 fetcher 插件
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import sys
import importlib
from threading import Thread

from helper.proxy import Proxy
from helper.check import DoValidator
from handler.logHandler import LogHandler
from handler.configHandler import ConfigHandler
from fetcher.baseFetcher import BaseFetcher


def _get_sources_dir():
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', 'fetcher', 'sources')


def _load_fetcher_class(class_name):
    """
    动态加载 fetcher 类，支持运行时热更新。
    每次调用重新 import module，确保读到文件最新版本。
    """
    sources_dir = _get_sources_dir()
    for filename in os.listdir(sources_dir):
        if not filename.endswith('.py') or filename.startswith('_'):
            continue
        module_name = "fetcher.sources.%s" % filename[:-3]
        try:
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
            fetcher_class = getattr(module, class_name, None)
            if fetcher_class and issubclass(fetcher_class, BaseFetcher):
                return fetcher_class
        except Exception:
            continue
    return None


def _discover_fetchers(exclude_list):
    """
    自动扫描 sources/ 目录，返回所有 enabled=True 且不在黑名单中的 fetcher 类名列表。
    每次调用重新加载模块，支持运行时热更新。
    """
    sources_dir = _get_sources_dir()
    fetcher_names = []
    for filename in os.listdir(sources_dir):
        if not filename.endswith('.py') or filename.startswith('_'):
            continue
        module_name = "fetcher.sources.%s" % filename[:-3]
        try:
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)
            for attr_name in dir(module):
                attr = getattr(module, attr_name, None)
                if (attr and isinstance(attr, type)
                        and issubclass(attr, BaseFetcher)
                        and attr is not BaseFetcher
                        and attr.name
                        and attr.enabled
                        and attr.__name__ not in exclude_list):
                    fetcher_names.append(attr.__name__)
        except Exception:
            continue
    return sorted(fetcher_names)


class _ThreadFetcher(Thread):

    def __init__(self, fetcher_class, proxy_dict):
        Thread.__init__(self)
        self.fetcher_class = fetcher_class
        self.proxy_dict = proxy_dict
        self.log = LogHandler("fetcher")

    def run(self):
        fetcher_name = self.fetcher_class.name
        self.log.info("ProxyFetch - {func}: start".format(func=fetcher_name))
        try:
            for proxy in self.fetcher_class().fetch():
                self.log.info('ProxyFetch - %s: %s ok' % (fetcher_name, proxy.ljust(23)))
                proxy = proxy.strip()
                if proxy in self.proxy_dict:
                    self.proxy_dict[proxy].add_source(fetcher_name)
                else:
                    self.proxy_dict[proxy] = Proxy(
                        proxy, source=fetcher_name)
        except Exception as e:
            self.log.error("ProxyFetch - {func}: error".format(func=fetcher_name))
            self.log.error(str(e))


class Fetcher(object):
    name = "fetcher"

    def __init__(self):
        self.log = LogHandler(self.name)
        self.conf = ConfigHandler()

    def run(self):
        """
        fetch proxy with fetcher plugins
        :return:
        """
        proxy_dict = dict()
        thread_list = list()
        self.log.info("ProxyFetch : start")

        exclude_list = self.conf.fetcherExclude
        fetcher_names = _discover_fetchers(exclude_list)
        self.log.info("ProxyFetch : active fetchers [%s]" % ", ".join(fetcher_names))

        for fetcher_name in fetcher_names:
            fetcher_class = _load_fetcher_class(fetcher_name)
            if not fetcher_class:
                self.log.error("ProxyFetch - {func}: class not exists!".format(func=fetcher_name))
                continue
            thread_list.append(_ThreadFetcher(fetcher_class, proxy_dict))

        for thread in thread_list:
            thread.setDaemon(True)
            thread.start()

        for thread in thread_list:
            thread.join()

        self.log.info("ProxyFetch - all complete!")
        for _ in proxy_dict.values():
            if DoValidator.preValidator(_.proxy):
                yield _
