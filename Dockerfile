FROM python:3.6-alpine

MAINTAINER jhao104 <j_hao104@163.com>

ENV TZ Asia/Shanghai

WORKDIR /app

COPY ./requirements.txt .

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories

RUN apk add musl-dev gcc libxml2-dev libxslt-dev && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    apk del gcc musl-dev

COPY . .

EXPOSE 5010

WORKDIR /app/cli

ENTRYPOINT [ "sh", "start.sh" ]
