FROM registry.cn-beijing.aliyuncs.com/staugur/python:supervisor
MAINTAINER taochengwei <staugur@saintic.com>
ENV REGISTRY https://pypi.org/simple
ADD src /Tdi
ADD supervisord.conf /etc/supervisord.conf
RUN yum install -y gcc python-devel libffi-devel && pip install -i $REGISTRY -r /Tdi/requirements.txt && chmod +x /Tdi/cleanDownload.py && ln -sf /Tdi/cleanDownload.py /usr/bin/cleanDownload.py
WORKDIR /Tdi
ENTRYPOINT ["supervisord", "-c", "/etc/supervisord.conf"]