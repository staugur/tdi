FROM alpine
MAINTAINER taochengwei <staugur@saintic.com>
ADD src /Tdi
ADD localtime /etc/localtime
ADD supervisord.conf /etc/supervisord.conf
RUN ls -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN apk add --update python python-dev py-pip libffi-dev && rm /var/cache/apk/
RUN echo "supervisor" >> /Tdi/requirements.txt
RUN pip install --index https://pypi.douban.com/simple/ -r /Tdi/requirements.txt
WORKDIR /Tdi
ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]