#!/usr/bin/env python
from cocaine.worker import Worker

from profile import get

W = Worker()

W.run({"get": get})