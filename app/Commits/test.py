#!/usr/bin/env python
import msgpack

from cocaine.services import Service

COMMIT = {
	"id": "AAAA",
	"app": "dsds",
	"page": 1,
	"status": "ok",
	"summary": "sd"
}


print(Service('flow-commit').enqueue('store_commit', msgpack.packb(COMMIT)).get())
print(Service('flow-commit').enqueue('find_commit', msgpack.packb(COMMIT)).get())

COMMIT['status'] = 'checkouted'
print(Service('flow-commit').enqueue('update_commit', msgpack.packb(COMMIT)).get())
COMMIT['status'] = 'ok'
print(Service('flow-commit').enqueue('find_commit', msgpack.packb(COMMIT)).get())
