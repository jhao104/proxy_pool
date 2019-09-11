FROM python:3.6

MAINTAINER jhao104 <j_hao104@163.com>

ENV TZ Asia/Shanghai

WORKDIR /usr/src/app

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY . .

EXPOSE 5010

WORKDIR /usr/src/app/cli

ENTRYPOINT [ "sh", "start.sh" ]
