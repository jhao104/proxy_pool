# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     six
   Description :
   Author :        JHao
   date：          2020/6/22
-------------------------------------------------
   Change Activity:
                   2020/6/22:
-------------------------------------------------
"""
__author__ = 'JHao'

import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    def iteritems(d, **kw):
        return iter(d.items(**kw))
else:
    def iteritems(d, **kw):
        return d.iteritems(**kw)


if PY3:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

if PY3:
    from imp import reload as reload_six
else:
    reload_six = reload

if PY3:
    from queue import Empty, Queue
else:
    from Queue import Empty, Queue
