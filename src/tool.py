# -*- coding: utf-8 -*-
"""
    CrawlHuabanTdi.tool
    ~~~~~~~~~~~~~~~~~~~

    工具

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

import os
import sys
import time
import datetime
import requests
import logging
import logging.handlers
from redis import from_url
from config import LOGLEVEL, REDIS, PROCNAME
from version import __version__
PY2 = sys.version_info[0] == 2
if PY2:
    string_types = (str, unicode)
    makeLong = long
else:
    string_types = (str,)
    makeLong = int


rc = from_url(REDIS)


def get_current_timestamp():
    """ 获取本地当前时间戳(10位): Unix timestamp：是从1970年1月1日（UTC/GMT的午夜）开始所经过的秒数，不考虑闰秒 """
    return int(time.time())


def timestamp_after_timestamp(timestamp=None, seconds=0, minutes=0, hours=0, days=0):
    """ 给定时间戳(10位),计算该时间戳之后多少秒、分钟、小时、天的时间戳(本地时间) """
    # 1. 默认时间戳为当前时间
    timestamp = get_current_timestamp() if timestamp is None else timestamp
    # 2. 先转换为datetime
    d1 = datetime.datetime.fromtimestamp(timestamp)
    # 3. 根据相关时间得到datetime对象并相加给定时间戳的时间
    d2 = d1 + datetime.timedelta(seconds=int(seconds), minutes=int(minutes), hours=int(hours), days=int(days))
    # 4. 返回某时间后的时间戳
    return int(time.mktime(d2.timetuple()))


def memRate():
    mem = {}
    with open("/proc/meminfo") as f:
        lines = f.readlines()
    for line in lines:
        if len(line) < 2:
            continue
        name = line.split(':')[0]
        var = line.split(':')[1].split()[0]
        mem[name] = makeLong(var) * 1024.0
    return round(100 * int(mem['MemTotal'] - mem['MemFree'] - mem['Buffers'] - mem['Cached']) / int(mem["MemTotal"]), 2)


def loadStat():
    """Return load value in 5 minutes(float)"""
    return os.getloadavg()[1]


def diskRate(path=None, ret="percent"):
    """Return disk usage statistics about the given path.

    Will return the namedtuple with attributes: 'total', 'used' and 'free',
    which are the amount of total, used and free space, in bytes.
    """
    vfs = os.statvfs(path or os.getcwd())
    #Total,总容量
    total = vfs.f_bsize*vfs.f_blocks
    #Used,使用量，总容量减去空闲容量
    used = vfs.f_bsize * (vfs.f_blocks - vfs.f_bfree)
    #Available,有效容量
    available = vfs.f_bsize * vfs.f_bavail
    #使用量百分比
    percent = round( float(used) / float(used+available) * 100 + 1, 2)
    return percent if ret == "percent" else dict(total=total, available=available, used=used, percent=percent)


def makedir(d):
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
                if os.path.splitext(filename)[-1] not in exclude:
                    zf.write(os.path.join(zip_path, filename), filename.decode())
                    # 写入压缩文件后直接删除源文件，经测试对压缩文件无影响
                    os.remove(os.path.join(zip_path, filename))
        return zip_filename if os.path.isabs(zip_filename) else os.path.join(os.getcwd(), zip_filename)
    else:
        raise TypeError


def make_tarfile(tar_filename, tar_path, exclude=[]):
    """
    :param tar_filename: str: packaged file name
    :param tar_path: str: The packaged directory (the files in this directory will be packaged)
    "param exclude: list,tuple: File suffixes will not be packaged in this list when packaged
    """
    if tar_filename and tar_path and \
            os.path.splitext(tar_filename)[-1] == ".tar" and \
            os.path.isdir(tar_path) and \
            isinstance(exclude, (list, tuple)):
        try:
            import tarfile
        except ImportError:
            raise
        with tarfile.open(tar_filename, "w") as tar:
            for fn in os.listdir(tar_path):
                fullpath = os.path.join(tar_path, fn)
                if os.path.isdir(fullpath):
                    continue
                if os.path.splitext(fn)[-1] not in exclude:
                    tar.add(fullpath, fn)
                    os.remove(fullpath)
        return tar_filename if os.path.isabs(tar_filename) else os.path.join(os.getcwd(), tar_filename)
    else:
        raise TypeError


def getDirSize(dir_path, exclude=[]):
    size = 0L
    for root, dirs, files in os.walk(dir_path):
        size += sum([os.path.getsize(os.path.join(root, name)) for name in files if os.path.splitext(name)[-1] not in exclude ])
    return size


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
        return "%.2fK" % (kb)


def try_request(url, params=None, data=None, timeout=5, num_retries=1, method='post'):
    """
    @params dict: 请求查询参数
    @data dict: 提交表单数据
    @timeout int: 超时时间，单位秒
    @num_retries int: 超时重试次数
    """
    headers = {"User-Agent": "Mozilla/5.0 (X11; CentOS; Linux i686; rv:7.0.1406) Gecko/20100101 %s/%s" % (PROCNAME, __version__)}
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
        self.logFile = os.path.join(self.log_dir, '%s.log' % self.logName)
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
        self._logger.setLevel(self._levels.get(LOGLEVEL, logging.INFO))

    @property
    def getLogger(self):
        return self._logger
