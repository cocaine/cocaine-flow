#!/usr/bin/env python
from cocaine.worker import Worker

from commit import *

W = Worker()

W.run({"find_commit": commit_find,
       "update_commit": commit_update,
       "store_commit": commit_store,
       "get_summary": summary_get,
       "update_summary": summary_update})
