FROM python:2.7

WORKDIR /usr/src/app

COPY . .

ENV DEBIAN_FRONTEND noninteractive
ENV TZ Asia/Shanghai

RUN pip install --no-cache-dir -r requirements.txt && \
	apt-get update && \
	apt-get install -y --force-yes git make gcc g++ autoconf && apt-get clean && \
	git clone --depth 1 https://github.com/ideawu/ssdb.git ssdb && \
	cd ssdb && make && make install && cp ssdb-server /usr/bin && \
	apt-get remove -y --force-yes git make gcc g++ autoconf && \
	apt-get autoremove -y && \
	rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
	cp ssdb.conf /etc && cd .. && yes | rm -r ssdb && \

	mkdir -p /var/lib/ssdb && \
	sed \
		-e 's@home.*@home /var/lib@' \
		-e 's/loglevel.*/loglevel info/' \
		-e 's@work_dir = .*@work_dir = /var/lib/ssdb@' \
		-e 's@pidfile = .*@pidfile = /run/ssdb.pid@' \
		-e 's@level:.*@level: info@' \
		-e 's@ip:.*@ip: 0.0.0.0@' \
		-i /etc/ssdb.conf && \

	echo "# ! /bin/sh " > /usr/src/app/run.sh && \
	echo "cd Run" >> /usr/src/app/run.sh && \
	echo "/usr/bin/ssdb-server /etc/ssdb.conf &" >> /usr/src/app/run.sh && \
	echo "python main.py" >> /usr/src/app/run.sh && \

	chmod 777 run.sh

EXPOSE 5000

CMD [ "sh", "run.sh" ]