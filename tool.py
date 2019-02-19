# -*- coding: utf-8 -*-
"""
    CrawlHuabanTdi.tool
    ~~~~~~~~~~~~~~~~~~~

    工具

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

import os
import time
import requests
import logging
import logging.handlers
from redis import from_url
from config import LOGLEVEL, REDIS
from version import __version__

rc = from_url(REDIS)


def get_current_timestamp():
    """ 获取本地当前时间戳(10位): Unix timestamp：是从1970年1月1日（UTC/GMT的午夜）开始所经过的秒数，不考虑闰秒 """
    return int(time.time())


def memRate():
    mem = {}
    with open("/proc/meminfo") as f:
        lines = f.readlines()
    for line in lines:
        if len(line) < 2:
            continue
        name = line.split(':')[0]
        var = line.split(':')[1].split()[0]
        mem[name] = long(var) * 1024.0
    mem['MemUsed'] = mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']
    return 100 * int(mem["MemTotal"]-mem['MemUsed']) / int(mem["MemTotal"])


def loadStat():
    loadavg = {}
    with open("/proc/loadavg") as f:
        con = f.read().split()
    loadavg['lavg_1'] = con[0]
    loadavg['lavg_5'] = con[1]
    loadavg['lavg_15'] = con[2]
    return loadavg['lavg_5']


def diskRate(path=None):
    disk = os.statvfs(path or os.getcwd())
    percent = (disk.f_blocks - disk.f_bfree) * 100 / (disk.f_blocks - disk.f_bfree + disk.f_bavail) + 1
    return percent


def makedir(d):
    d = str(d)
    if not os.path.exists(d):
        os.makedirs(d)
    if os.path.exists(d):
        return True
    else:
        return False


def make_zipfile(zip_filename, zip_path, exclude=[]):
    """Create a zipped file with the name zip_filename. Compress the files in the zip_path directory. Do not include subdirectories. Exclude files in the exclude file.
    @param zip_filename str: Compressed file name
    @param zip_path str: The compressed directory (the files in this directory will be compressed)
    @param exclude list,tuple: File suffixes will not be compressed in this list when compressed
    """
    if zip_filename and os.path.splitext(zip_filename)[-1] == ".zip" and zip_path and os.path.isdir(zip_path) and isinstance(exclude, (list, tuple)):
        try:
            import zipfile
        except ImportError:
            raise
        with zipfile.ZipFile(zip_filename, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for filename in os.listdir(zip_path):
                if os.path.isdir(filename):
                    continue
                if not os.path.splitext(filename)[-1] in exclude:
                    zf.write(os.path.join(zip_path, filename), filename)
        return zip_filename if os.path.isabs(zip_filename) else os.path.join(os.getcwd(), zip_filename)
    else:
        raise TypeError


def formatSize(bytes):
    # 字节bytes转化kb\m\g
    try:
        bytes = float(bytes)
        kb = bytes / 1024
    except:
        return "Error"
    if kb >= 1024:
        M = kb / 1024
        if M >= 1024:
            G = M / 1024
            return "%.2fG" % (G)
        else:
            return "%.2fM" % (M)
    else:
        return "%.2fkb" % (kb)


def try_request(url, params=None, data=None, timeout=5, num_retries=1, method='post'):
    """
    @params dict: 请求查询参数
    @data dict: 提交表单数据
    @timeout int: 超时时间，单位秒
    @num_retries int: 超时重试次数
    """
    headers = {"User-Agent": "Mozilla/5.0 (X11; CentOS; Linux i686; rv:7.0.1406) Gecko/20100101 CrawlHuabanTdi/{}".format(__version__)}
    method_func = requests.get if method == 'get' else requests.post
    try:
        resp = method_func(url, params=params, headers=headers, timeout=timeout, data=data).json()
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        if num_retries > 0:
            return try_request(url, params=params, data=data, timeout=timeout, num_retries=num_retries-1)
    except Exception:
        raise
    else:
        return resp


class Logger:

    def __init__(self, logName, backupCount=10):
        self.logName = logName
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        self.logFile = os.path.join(self.log_dir, '{0}.log'.format(self.logName))
        self._levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self._logfmt = '%Y-%m-%d %H:%M:%S'
        self._logger = logging.getLogger(self.logName)
        makedir(self.log_dir)

        handler = logging.handlers.TimedRotatingFileHandler(filename=self.logFile,
                                                            backupCount=backupCount,
                                                            when="midnight")
        handler.suffix = "%Y%m%d"
        formatter = logging.Formatter('[ %(levelname)s ] %(asctime)s %(filename)s:%(lineno)d %(message)s', datefmt=self._logfmt)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        self._logger.setLevel(self._levels.get(LOGLEVEL))

    @property
    def getLogger(self):
        return self._logger
