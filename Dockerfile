FROM python:3.6
ENV DEBIAN_FRONTEND noninteractive
ENV TZ Asia/Shanghai
WORKDIR /usr/src/app
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5010
WORKDIR /usr/src/app/
CMD [ "python", "Run/main.py" ]
