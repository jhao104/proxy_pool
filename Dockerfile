FROM python:3.6-slim

MAINTAINER ndiy.gm@gmail.com

ENV TZ Asia/Shanghai

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY . .
VOLUME [ "/usr/src/app/Config", "/usr/src/app/ProxyGetter" ]
EXPOSE 5010

WORKDIR /usr/src/app/cli

ENTRYPOINT [ "sh", "start.sh" ]
