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
-------------------------------------------------
"""
__author__ = 'JHao'

import platform
from random import shuffle
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

from util.six import iteritems
from helper.proxy import Proxy
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
    {"url": "/get", "params": "type: ''https'|'', count: '1', region: 'e.g. CN'", "desc": "get proxy"},
    {"url": "/pop", "params": "type: ''https'|'', region: 'e.g. CN'", "desc": "get and delete a proxy"},
    {"url": "/delete", "params": "proxy: 'e.g. 127.0.0.1:8080'", "desc": "delete an unable proxy"},
    {"url": "/all", "params": "type: ''https'|'', region: 'e.g. CN'", "desc": "get all proxy from proxy pool"},
    {"url": "/count", "params": "region: 'e.g. CN'", "desc": "return proxy count"}
    # 'refresh': 'refresh proxy pool',
]


def _get_https_arg():
    return request.args.get("type", "").lower() == 'https'


def _get_region_arg():
    return request.args.get("region", "").strip()


def _get_count_arg(default=1):
    try:
        return max(int(request.args.get("count", default)), 1)
    except (TypeError, ValueError):
        return default


def _filter_region(proxies, region):
    if not region:
        return proxies
    region = region.lower()
    return [proxy for proxy in proxies if str(proxy.region).lower() == region]


def _get_filtered_proxies(https=False, region=""):
    return _filter_region(proxy_handler.getAll(https), region)


@app.route('/')
def index():
    return {'url': api_list}


@app.route('/get/')
def get():
    https = _get_https_arg()
    region = _get_region_arg()
    count = _get_count_arg()
    if count == 1 and not region:
        proxy = proxy_handler.get(https)
        return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}

    proxies = _get_filtered_proxies(https, region)
    if not proxies:
        return {"code": 0, "src": "no proxy"}
    shuffle(proxies)
    result = [proxy.to_dict for proxy in proxies[:count]]
    return result[0] if count == 1 else jsonify(result)


@app.route('/pop/')
def pop():
    https = _get_https_arg()
    region = _get_region_arg()
    if region:
        proxies = _get_filtered_proxies(https, region)
        shuffle(proxies)
        proxy = proxies[0] if proxies else None
        if proxy:
            proxy_handler.delete(proxy)
    else:
        proxy = proxy_handler.pop(https)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    return 'success'


@app.route('/all/')
def getAll():
    https = _get_https_arg()
    region = _get_region_arg()
    proxies = _get_filtered_proxies(https, region)
    return jsonify([_.to_dict for _ in proxies])


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    status = proxy_handler.delete(Proxy(proxy))
    return {"code": 0, "src": status}


@app.route('/count/')
def getCount():
    proxies = _get_filtered_proxies(region=_get_region_arg())
    http_type_dict = {}
    source_dict = {}
    for proxy in proxies:
        http_type = 'https' if proxy.https else 'http'
        http_type_dict[http_type] = http_type_dict.get(http_type, 0) + 1
        for source in proxy.source.split('/'):
            source_dict[source] = source_dict.get(source, 0) + 1
    return {"http_type": http_type_dict, "source": source_dict, "count": len(proxies)}


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
