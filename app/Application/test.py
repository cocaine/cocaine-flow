#!/usr/bin/env python
import msgpack

from cocaine.services import Service

REPO_INFO = {
	"repository": "https://github.com/noxiouz/flask-cocaine-pycon.git",
	"reference": "",
	"type": "git"
}

print(Service("flow-app").enqueue("get", "").get())
for i in Service("flow-app").enqueue("upload", msgpack.packb(REPO_INFO)):
    print i
#print(Service("flow-app").enqueue("delete", msgpack.packb({"id": "flask-cocaine-pycon_HEAD"})).get())
