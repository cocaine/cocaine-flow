#!/usr/bin/env python

from cocaine.worker import Worker
from app import get

W = Worker()

W.run({"get": get})