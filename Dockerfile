FROM python:3.6-alpine

# MAINTAINER jhao104 <j_hao104@163.com>

ENV TIMEZONE Asia/Shanghai

WORKDIR /app

COPY . .
# COPY ./requirements.txt .

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories && \
    apk --update add --no-cache musl-dev gcc libxml2-dev libxslt-dev tzdata && \
    cp /usr/share/zoneinfo/${TIMEZONE} /etc/localtime && \
    pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    apk del musl-dev gcc tzdata && \
    mkdir -p /usr/share/zoneinfo/${TIMEZONE} && rm -rf /usr/share/zoneinfo/${TIMEZONE} && ln -s /etc/localtime /usr/share/zoneinfo/${TIMEZONE}

EXPOSE 5010

ENTRYPOINT [ "sh", "start.sh" ]
