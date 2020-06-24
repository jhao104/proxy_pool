# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxy_pool
   Description :   proxy pool 启动入口
   Author :        JHao
   date：          2020/6/19
-------------------------------------------------
   Change Activity:
                   2020/6/19:
-------------------------------------------------
"""
__author__ = 'JHao'

import click

from util import six
from config.setting import BANNER

# from Schedule.ProxyScheduler import runScheduler
from api.proxyApi import runFlask

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='2.1.0')
def cli():
    """ProxyPool cli工具"""


@cli.command(name="schedule")
def schedule():
    """ 启动调度程序 """
    click.echo(BANNER)
    # runScheduler()


@cli.command(name="server")
def schedule():
    """ 启动api服务 """
    # click.echo(BANNER)
    # runFlask()
    from test import testProxyFetcher
    testProxyFetcher.test()


if __name__ == '__main__':
    cli()
