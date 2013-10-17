#!/usr/bin/env python
from cocaine.worker import Worker

from commit import *

W = Worker()

W.run({"find": find,
	   "update": update,
	   "store": store})
