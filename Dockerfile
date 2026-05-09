FROM python:3.6-alpine

# 设置标签
LABEL name="proxy-pool" \
      version="1.0.0" \
      project="ci" \
      platform="linux/amd64,linux/arm64" \
      maintainer="andy" \
      description="Proxy Pool Service"

MAINTAINER jhao104 <j_hao104@163.com>

WORKDIR /app

COPY ./requirements.txt .

# apk repository
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories

# timezone
RUN apk add -U tzdata && cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && apk del tzdata

# runtime environment
RUN apk add musl-dev gcc libxml2-dev libxslt-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc musl-dev

COPY . .

EXPOSE 5010

ENTRYPOINT [ "sh", "start.sh" ]
