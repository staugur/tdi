# -*- coding: utf-8 -*-
"""
    CrawlHuabanTdi
    ~~~~~~~~~~~~~~

    花瓣网、堆糖网下载程序的远端下载服务。

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

import os
import json
import hashlib
from rq import Queue
from functools import wraps
from flask import Flask, request, jsonify
from qf import DownloadBoard
from tool import memRate, loadStat, diskRate, makedir, get_current_timestamp, rc, timestamp_after_timestamp
from config import HOST, PORT, REDIS, TOKEN, STATUS, NORQDASH
from version import __version__

__author__ = 'staugur'
__email__ = 'staugur@saintic.com'
__date__ = '2019-02-16'

# Download pictures directory
DOWNLOADPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
makedir(DOWNLOADPATH)
asyncQueue = Queue(connection=rc)


def checkSignature(signature, timestamp, nonce):
    args = [TOKEN, timestamp, nonce]
    args.sort()
    # TypeError: Unicode-objects must be encoded before hashing  encode("utf8")
    mysig = hashlib.sha1(''.join(args).encode("utf8")).hexdigest()
    return mysig == signature


def signature_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        if not checkSignature(signature, timestamp, nonce):
            return jsonify(dict(code=1, msg="Invalid signature"))
        return f(*args, **kwargs)
    return decorated_function


# Initialization app
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.urandom(24),
    REDIS_URL=REDIS,
    RQ_POLL_INTERVAL=2500,
)
if NORQDASH != "yes":
    import rq_dashboard
    app.register_blueprint(rq_dashboard.blueprint, url_prefix="/rqdashboard")


@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE,OPTIONS'
    return response


@app.route("/ping")
@signature_required
def ping():
    res = dict(code=0, version=__version__, status=STATUS, memRate=memRate(), loadFive=loadStat(), diskRate=diskRate(DOWNLOADPATH), timestamp=get_current_timestamp(), rqcount=asyncQueue.count)
    return jsonify(res)


@app.route("/download", methods=["POST"])
@signature_required
def download():
    if request.method == "POST":
        res = dict(code=1, msg=None)
        data = request.form
        if "uifnKey" in data and "site" in data and "board_id" in data and "uifn" in data and "board_pins" in data and "etime" in data and "MAX_BOARD_NUMBER" in data and "CALLBACK_URL" in data:
            etime = int(data["etime"])
            # 存入缓存数据
            pipe = rc.pipeline()
            pipe.hmset(uifn, dict(etime=etime, CALLBACK_URL=data["CALLBACK_URL"], board_pins=data["board_pins"], MAX_BOARD_NUMBER=data["MAX_BOARD_NUMBER"], board_id=data["board_id"], site=data["site"], uifnKey=data["uifnKey"]))
            pipe.expireat(uifn, timestamp_after_timestamp(etime, hours=1))
            try:
                pipe.execute()
            except:
                res.update(msg="redis is error")
            else:
                res.update(code=0)
                asyncQueue.enqueue_call(func=DownloadBoard, args=(DOWNLOADPATH, data["uifn"]), timeout=3600)
        else:
            res.update(msg="Invalid param")
        return jsonify(res)


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=True)
