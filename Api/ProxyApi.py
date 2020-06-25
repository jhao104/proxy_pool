# -*- coding: utf-8 -*-
# !/usr/bin/env python
from Manager.ProxyManager import ProxyManager
from Config.ConfigGetter import config
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
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
import platform
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

sys.path.append('../')


app = Flask(__name__)


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = {
    'get': u'get an useful proxy',
    # 'refresh': u'refresh proxy pool',
    'get_all': u'get all proxy from proxy pool',
    'delete?proxy=127.0.0.1:8080': u'delete an unable proxy',
    'get_status': u'proxy number'
}


@app.route('/')
def index():
    return api_list


@app.route('/get/')
def get():
    proxy = ProxyManager().get()
    return proxy.info_json if proxy else {"code": 0, "src": "no proxy"}


@app.route('/get_socks/')
def get_socks():
    proxy = ProxyManager().get_socks()
    return proxy.info_json if proxy else {"code": 0, "src": "no proxy"}


@app.route('/get_http/')
def get_http():
    proxy = ProxyManager().get_http()
    return proxy.info_json if proxy else {"code": 0, "src": "no proxy"}


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    # ProxyManager().refresh()
    pass
    return 'success'


@app.route('/get_all/')
def getAll():
    proxies = ProxyManager().getAll()
    return jsonify([_.info_dict for _ in proxies])


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    ProxyManager().delete(proxy)
    return {"code": 0, "src": "success"}


@app.route('/get_status/')
def getStatus():
    status = ProxyManager().getNumber()
    return status


if platform.system() != "Windows":
    import gunicorn.app.base
    from six import iteritems

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


def runFlask():
    app.run(host=config.host_ip, port=config.host_port)


def runFlaskWithGunicorn():
    _options = {
        'bind': '%s:%s' % (config.host_ip, config.host_port),
        'workers': 4,
        'accesslog': '-',  # log to stdout
        'access_log_format': '%(h)s %(l)s %(t)s "%(r)s" %(s)s "%(a)s"'
    }
    StandaloneApplication(app, _options).run()


if __name__ == '__main__':
    if platform.system() == "Windows":
        runFlask()
    else:
        runFlaskWithGunicorn()
