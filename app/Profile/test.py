#!/usr/bin/env python

from cocaine.services import Service


print(Service("flow-profile").enqueue("get", "default").get())