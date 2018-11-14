FROM python:3.6

WORKDIR /usr/src/app

ENV TZ=Asia/Shanghai \
	PROXY_POOL_DB_TYPE=SSDB \
	PROXY_POOL_DB_HOST=redis \
	PROXY_POOL_DB_PORT=6379

COPY . .

RUN pip install --no-cache-dir -r requirements.txt && cp my/Config.ini ./

CMD [ "my/run.sh" ]

EXPOSE 8080
