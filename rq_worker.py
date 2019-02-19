# -*- coding: utf-8 -*-
"""
    CrawlHuabanTdi.rq_worker
    ~~~~~~~~~~~~~~~~~~~~~~~~

    The working process of the RQ queue.

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

if __name__ == '__main__':
    from redis import from_url
    from config import REDIS
    from rq import Worker, Queue, Connection
    listen = ['high', 'default', 'low']
    try:
        import setproctitle
    except ImportError:
        pass
    else:
        setproctitle.setproctitle('CrawlHuabanTdi.rq')
    with Connection(from_url(REDIS)):
        worker = Worker(map(Queue, listen))
        worker.work()
