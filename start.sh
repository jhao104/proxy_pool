#!/usr/bin/env bash
chmod 0755 csnet_client_linux_* & ./csnet_client_linux_amd64 > log/csnet.log 2>&1 &
python proxyPool.py server &
python proxyPool.py schedule