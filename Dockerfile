FROM registry.cn-beijing.aliyuncs.com/staugur/python:supervisor
MAINTAINER taochengwei <staugur@saintic.com>
ADD src /Tdi
ADD supervisord.conf /etc/supervisord.conf
RUN pip install -r /Tdi/requirements.txt
WORKDIR /Tdi
ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]