FROM python:3.6-alpine

MAINTAINER jhao104 <j_hao104@163.com>

ENV TZ Asia/Shanghai

WORKDIR /app

COPY ./requirements.txt .

RUN apk add musl-dev gcc libxml2-dev libxslt-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev

COPY . .

EXPOSE 5010

WORKDIR /app/cli

ENTRYPOINT [ "sh", "start.sh" ]
