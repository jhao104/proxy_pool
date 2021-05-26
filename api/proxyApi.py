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
-------------------------------------------------
"""
__author__ = 'JHao'

import platform
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
    {"url": "/get", "params": "type: ''https'|''", "desc": "get a proxy"},
    {"url": "/pop", "params": "", "desc": "get and delete a proxy"},
    {"url": "/delete", "params": "proxy: 'e.g. 127.0.0.1:8080'", "desc": "delete an unable proxy"},
    {"url": "/all", "params": "type: ''https'|''", "desc": "get all proxy from proxy pool"},
    {"url": "/count", "params": "", "desc": "return proxy count"}
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
    status = proxy_handler.getCount()
    return status


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
