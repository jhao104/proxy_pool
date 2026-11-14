# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :   WebApi
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/04: WebApi
                   2019/08/14: 集成Gunicorn启动方式
                   2020/06/23: 新增pop接口
                   2022/07/21: 更新count接口
                   2026/08/30: 新增/count/source按来源统计接口
                   2026/11/14: /count/source 增加抓取数/可用数/存活率/上次抓取时间
                   2026/11/14: 新增 /count/speed 校验速度统计接口
-------------------------------------------------
"""
__author__ = 'JHao'

import platform
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

from util.six import iteritems
from helper.proxy import Proxy
from helper.speedStat import SpeedStat
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler

app = Flask(__name__)
conf = ConfigHandler()
proxy_handler = ProxyHandler()


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = [
    {"url": "/get", "params": "type: ''https'|''", "desc": "get a proxy"},
    {"url": "/pop", "params": "", "desc": "get and delete a proxy"},
    {"url": "/delete", "params": "proxy: 'e.g. 127.0.0.1:8080'", "desc": "delete an unable proxy"},
    {"url": "/all", "params": "type: ''https'|''", "desc": "get all proxy from proxy pool"},
    {"url": "/count", "params": "", "desc": "return proxy count"},
    {"url": "/count/source", "params": "", "desc": "return proxy count by fetcher source"},
    {"url": "/count/speed", "params": "", "desc": "return check speed in 1/5/10 minutes"}
    # 'refresh': 'refresh proxy pool',
]


@app.route('/')
def index():
    return {'url': api_list}


@app.route('/get/')
def get():
    https = request.args.get("type", "").lower() == 'https'
    proxy = proxy_handler.get(https)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/pop/')
def pop():
    https = request.args.get("type", "").lower() == 'https'
    proxy = proxy_handler.pop(https)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    return 'success'


@app.route('/all/')
def getAll():
    https = request.args.get("type", "").lower() == 'https'
    proxies = proxy_handler.getAll(https)
    return jsonify([_.to_dict for _ in proxies])


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    status = proxy_handler.delete(Proxy(proxy))
    return {"code": 0, "src": status}


@app.route('/count/')
def getCount():
    proxies = proxy_handler.getAll()
    http_type_dict = {}
    source_dict = {}
    for proxy in proxies:
        http_type = 'https' if proxy.https else 'http'
        http_type_dict[http_type] = http_type_dict.get(http_type, 0) + 1
        for source in proxy.source.split('/'):
            source_dict[source] = source_dict.get(source, 0) + 1
    return {"http_type": http_type_dict, "source": source_dict, "count": len(proxies)}


@app.route('/count/source/')
def countSource():
    """
    按代理来源(采集fetcher)统计, 每个来源返回:
        pool_count        当前池中该来源贡献的可用代理数(多来源代理在各来源下分别计数)
        fetched           最近一轮抓取到的数量(已按源去重)
        valid             最近一轮抓取后验证通过的数量
        survival_rate     存活率 = valid / fetched
        last_fetch_time   最近一次抓取时间
    抓取统计来自 schedule 进程采集后写入数据库, server 重启后仍可读
    """
    proxies = proxy_handler.getAll()
    pool_dict = {}
    for proxy in proxies:
        for source in proxy.source.split('/'):
            if not source:
                continue
            pool_dict[source] = pool_dict.get(source, 0) + 1

    stat_dict = proxy_handler.getSourceStat()

    result = {}
    for source in set(pool_dict) | set(stat_dict):
        stat = stat_dict.get(source, {})
        fetched = stat.get("fetched", 0)
        valid = stat.get("valid", 0)
        result[source] = {
            "pool_count": pool_dict.get(source, 0),
            "fetched": fetched,
            "valid": valid,
            "survival_rate": round(float(valid) / fetched, 4) if fetched else 0.0,
            "last_fetch_time": stat.get("last_fetch_time", ""),
        }
    return {"source": result, "count": len(proxies)}


@app.route('/count/speed/')
def countSpeed():
    """
    校验速度统计: 最近 1/5/10 分钟内校验的 ip 数量与实际速度
    时间戳由 schedule 进程写入数据库, 窗口按查询时刻滑动计算
        {"1min": {"count": N, "speed": 个/秒}, "5min": {...}, "10min": {...}}
    """
    events = proxy_handler.getSpeedStat()
    return {"speed": SpeedStat.summarize(events)}


def runFlask():
    if platform.system() == "Windows":
        app.run(host=conf.serverHost, port=conf.serverPort)
    else:
        import gunicorn.app.base

        class StandaloneApplication(gunicorn.app.base.BaseApplication):

            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super(StandaloneApplication, self).__init__()

            def load_config(self):
                _config = dict([(key, value) for key, value in iteritems(self.options)
                                if key in self.cfg.settings and value is not None])
                for key, value in iteritems(_config):
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        _options = {
            'bind': '%s:%s' % (conf.serverHost, conf.serverPort),
            'workers': 4,
            'accesslog': '-',  # log to stdout
            'access_log_format': '%(h)s %(l)s %(t)s "%(r)s" %(s)s "%(a)s"'
        }
        StandaloneApplication(app, _options).run()


if __name__ == '__main__':
    runFlask()
