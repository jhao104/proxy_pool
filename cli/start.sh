#!/usr/bin/env bash
python3 proxyPool.py webserver &
python3 proxyPool.py schedule
