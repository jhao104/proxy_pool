FROM python:3.10-alpine

LABEL maintainer="jhao104 <j_hao104@163.com>"

WORKDIR /app

COPY ./requirements.txt .

# timezone and init process
RUN apk add -U tzdata tini && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    apk del tzdata

# runtime environment
RUN apk add musl-dev gcc libxml2-dev libxslt-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev

COPY . .

EXPOSE 5010

ENTRYPOINT ["tini", "--", "bash", "proxy_pool.sh", "start", "--fg"]
