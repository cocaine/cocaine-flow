#!/usr/bin/env python

from cocaine.services import Service

import msgpack
print(Service("flow-profile").enqueue("get", "default").get())
print(Service("flow-profile").enqueue("store", msgpack.packb(["TEST",{"A":1, "poolLimit": 100, "Z": None}])).get())
print(Service("flow-profile").enqueue("all", "").get())
print(Service("flow-profile").enqueue("delete", "TEST").get())
print(Service("flow-profile").enqueue("all", "").get())
