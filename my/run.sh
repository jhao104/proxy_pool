#!/bin/bash

for var in \
	PROXY_POOL_DB_TYPE \
	PROXY_POOL_DB_HOST \
	PROXY_POOL_DB_PORT \
; do
	val="${!var}"
	if [ "$val" ]; then
		sed -ri "s/$var/$val/" Config.ini
	fi
done

python Run/main.py