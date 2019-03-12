# -*- coding: utf-8 -*-
"""
    CrawlHuabanTdi.config
    ~~~~~~~~~~~~~~~~~~~~~

    The program configuration file, the preferred configuration item, reads the system environment variable first.

    :copyright: (c) 2019 by staugur.
    :license: BSD 3-Clause, see LICENSE for more details.
"""

from os import getenv

# Configuration Information:
# The getenv function first reads the configuration from the environment variable. When no variable is found, the default value is used.
# getenv("environment variable", "default value")
# Progranm Name
PROCNAME = "CrawlHuabanTdi"
# Program listening host
HOST = getenv("crawlhuabantdi_host", "127.0.0.1")
# Program listening port
PORT = int(getenv("crawlhuabantdi_port", 13145))
# Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGLEVEL = getenv("crawlhuabantdi_loglevel", "INFO")
# REDIS connection information in the format: redis://[:password]@host:port/db
REDIS = getenv("crawlhuabantdi_redis_url", "")
# Verification token filled in at the time of registration at the central end
TOKEN = getenv("crawlhuabantdi_token", "")
# Set this service status: ready or tardy
STATUS = getenv("crawlhuabantdi_status", "ready")
# Disable rq_dashboard
NORQDASH = getenv("crawlhuabantdi_norqdash", "no")
