# -*- coding: utf-8 -*-
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

from flask import Flask, jsonify, request
from Manager.ProxyManager import ProxyManager

app = Flask(__name__)

api_list = {
    'get': u'get an usable proxy',
    'refresh': u'refresh proxy pool',
    'get_all': u'get all proxy from proxy pool',
    'delete?proxy=127.0.0.1:8080': u'delete an unable proxy',
}


@app.route('/')
def index():
    return jsonify(api_list)

@app.route('/get/')
def get():
    proxy = ProxyManager().get()
    return proxy

@app.route('/refresh/')
def refresh():
    ProxyManager().refresh()
    return 'success'

@app.route('/get_all/')
def getAll():
    proxys = ProxyManager().getAll()
    return jsonify(proxys)

@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    ProxyManager().delete(proxy)
    return 'success'

if __name__ == '__main__':
    app.run()
