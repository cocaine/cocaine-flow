#!/usr/bin/env python
from cocaine.worker import Worker

from commit import *

W = Worker()


def ping(request, response):
    yield request.read()
    response.write("OK")
    response.close()

W.run({"find_commit": commit_find,
       "update_commit": commit_update,
       "store_commit": commit_store,
       "get_summary": summary_get,
       "update_summary": summary_update,
       "ping": ping})
