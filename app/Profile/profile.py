"""Operations with profiles"""
import msgpack

from cocaine.services import Service
from cocaine.logging import Logger
from cocaine.tools.actions import profile


storage = Service("storage")
LOGGER = Logger()


def get(request, response):
    name = yield request.read()
    raw_data = yield profile.View(storage, name).execute()
    data = msgpack.unpackb(raw_data)
    LOGGER.info("Get profile: %s %s" % (name, data))
    data['id'] = name
    data['name'] = name
    response.write(data)
    response.close()


def p_list(request, response):
    yield request.read()
    items = yield profile.List(storage).execute()
    p_all = list()
    for item in items:
        raw_data = yield profile.View(storage, item).execute()
        data = msgpack.unpackb(raw_data)
        data['id'] = item
        data['name'] = item
        p_all.append(data)
    response.write(p_all)
    response.close()


def check_profile(prof):
    return dict((k, v) for k, v in prof.iteritems() if v is not None)

def store(request, response):
    inc = yield request.read()
    name, data = msgpack.unpackb(inc)
    yield profile.Upload(storage, name, check_profile(data)).execute()
    data['id'] = name
    data['name'] = name
    response.write(data)
    response.close()


def delete(request, response):
    name = yield request.read()
    yield profile.Remove(storage, name).execute()
    response.write({})
    response.close()


