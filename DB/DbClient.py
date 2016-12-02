# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     DbClient.py  
   Description :  DB工厂类
   Author :       JHao
   date：          2016/12/2
-------------------------------------------------
   Change Activity:
                   2016/12/2: 
-------------------------------------------------
"""
__author__ = 'JHao'


class DbClient(object):
    """
    DbClient
    """
    def __init__(self, db_type, name, host='localhost', port=8080, **kwargs):
        """
        init
        :param db_type: DB type
        :param name:
        :param host:
        :param port:
        :param kwargs:
        :return:
        """

        __type = None
        if "ssdb" in db_type.lower():
            __type = "SsdbClient"
        else:
            pass
        assert __type, 'type error, Not support DB type: {}'.format(db_type)

        self.client = getattr(__import__(__type), __type)(name=name, host=host, port=port, **kwargs)

    def get(self, **kwargs):
        return self.client.get(**kwargs)

    def put(self, **kwargs):
        return self.client.put(**kwargs)

    def pop(self, **kwargs):
        return self.client.pop(**kwargs)


if __name__ == "__main__":
    account = DbClient('SSDB').pop()
    print(account)
