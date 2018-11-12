# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/4:
-------------------------------------------------
"""
__author__ = 'JHao'

import sys
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

sys.path.append('../')

from Util.GetConfig import config
from Manager.ProxyManager import ProxyManager

app = Flask(__name__)


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = {
    'get': u'get an usable proxy',
    # 'refresh': u'refresh proxy pool',
    'get_all': u'get all proxy from proxy pool',
    'delete?proxy=127.0.0.1:8080': u'delete an unable proxy',
    'get_status': u'proxy statistics'
}


@app.route('/')
def index():
    return api_list


@app.route('/get/')
def get():
    proxy = ProxyManager().get()
    return proxy if proxy else 'no proxy!'


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    # ProxyManager().refresh()
    pass
    return 'success'


@app.route('/get_all/')
def getAll():
    proxies = ProxyManager().getAll()
    return proxies


@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    ProxyManager().delete(proxy)
    return 'success'


@app.route('/get_status/')
def getStatus():
    status = ProxyManager().getNumber()
    return status


def run():
    if sys.platform.startswith("win"):
        app.run(host=config.host_ip, port=config.host_port)
    else:
        app.run(host=config.host_ip, port=config.host_port, threaded=False, processes=config.processes)


if __name__ == '__main__':
    run()
