#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    cleanDownload
    ~~~~~~~~~~~~~

    Cli Entrance

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

import os
import requests
from tool import rc, get_current_timestamp, timestamp_after_timestamp, try_request, Logger

logger = Logger("cli").getLogger


def execute_cleanDownload(hours=12):
    downloadDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "downloads")
    for uifn in os.listdir(downloadDir):
        filepath = os.path.join(downloadDir, uifn)
        if os.path.isfile(filepath) and os.path.splitext(uifn)[-1] == ".zip":
            try:
                if uifn.count("_") == 2:
                    aid, mst, _ = os.path.splitext(uifn)[0].split("_")
                else:
                    aid, mst = os.path.splitext(uifn)[0].split("_")
                assert len(mst) == 13
                mst = int(mst)
            except:
                pass
            else:
                if aid == "hb":
                    # 中心端接收到请求时的时间戳
                    ctime = mst / 1000
                    # 实际生成压缩文件时的时间戳
                    file_ctime = int(os.path.getctime(filepath))
                    if timestamp_after_timestamp(ctime, hours=hours) <= get_current_timestamp() and \
                        timestamp_after_timestamp(file_ctime, hours=hours) <= get_current_timestamp():
                        # 已过期，清理文件
                        try:
                            os.remove(filepath)
                            data = rc.hgetall(uifn)
                            if data and isinstance(data, dict):
                                resp = try_request(data[b"CALLBACK_URL"], timeout=5, params=dict(Action="SECOND_STATUS"), data=dict(uifn=uifn))
                                logger.info("Update expired status for %s, resp is %s" % (uifn, resp))
                                if resp.get("code") == 0:
                                    rc.delete(uifn)
                        except Exception as e:
                            logger.error(e, exc_info=True)
                        else:
                            logger.info("Remove zip file: {}".format(filepath))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--hours", default=12, type=int, choices=[3, 6, 12, 24], help="Expiration clearance limit for cleanDownload, default is 12.")
    args = parser.parse_args()
    hours = args.hours
    execute_cleanDownload(hours)
