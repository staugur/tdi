FROM registry.cn-beijing.aliyuncs.com/staugur/python:supervisor
MAINTAINER taochengwei <staugur@saintic.com>
ADD src /Tdi
ADD supervisord.conf /etc/supervisord.conf
RUN yum install -y gcc python-devel libffi-devel && pip install -r /Tdi/requirements.txt && chmod +x /Tdi/cleanDownload.py
WORKDIR /Tdi
ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]