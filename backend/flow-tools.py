#!/usr/bin/env python

import msgpack

from cocaine.services import Service
from cocaine.worker import Worker
from cocaine.asio.engine import asynchronous
from cocaine.logging import Logger
from cocaine.tools.actions import profile
from cocaine.tools.actions import runlist

from userdb import UserDB

ITEM_IS_ABSENT = -100

log = Logger()
storage = Service("storage")


db = UserDB(storage, "KEY", "TEST")


def unpacker(decoder):
    def dec(func):
        def wrapper(request, response):
            raw_req = yield request.read()
            decoded_req = decoder(raw_req)
            yield func(decoded_req, response)
        return wrapper
    return dec


# profiles
@unpacker(msgpack.unpackb)
@asynchronous
def profile_read(name, response):
    try:
        pf = yield profile.View(storage, name).execute()
        response.write(pf)
    except:
        response.error(ITEM_IS_ABSENT, "Profile %s is missing" % name)
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def profile_list(_, response):
    try:
        pf = yield profile.List(storage).execute()
        log.info("Profiles %s" % pf)
        response.write(pf)
    except:
        response.error(ITEM_IS_ABSENT, "Unable to list profiles")
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def profile_remove(name, response):
    try:
        yield profile.Remove(storage, name).execute()
    except:
        response.error(ITEM_IS_ABSENT, "Unable to remove profile")
    finally:
        response.close()


# runlist
@unpacker(msgpack.unpackb)
@asynchronous
def runlist_read(name, response):
    try:
        pf = yield runlist.View(storage, name).execute()
        response.write(pf)
    except Exception as err:
        log.error(str(err))
        response.error(ITEM_IS_ABSENT, "Runlist %s is missing" % name)
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def runlist_list(_, response):
    try:
        pf = yield runlist.List(storage).execute()
        response.write(pf)
    except:
        response.error(ITEM_IS_ABSENT, "Unable to list runlists")
    finally:
        response.close()


# hosts

HOSTS_TAG = ["flow-host"]
HOSTS_NAMESPACE = "flow-hosts"


@unpacker(msgpack.unpackb)
@asynchronous
def host_list(_, response):
    try:
        hosts = yield storage.find(HOSTS_NAMESPACE, HOSTS_TAG)
        response.write(hosts)
    except:
        response.error(ITEM_IS_ABSENT, "Unable to read hosts")
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def host_add(name, response):
    try:
        yield storage.write(HOSTS_NAMESPACE, name, name, HOSTS_TAG)
    except:
        response.error(ITEM_IS_ABSENT, "Unable to write host")
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def host_remove(name, response):
    try:
        yield storage.remove(HOSTS_NAMESPACE, name)
    except:
        response.error(ITEM_IS_ABSENT, "Unable to remove host")
    finally:
        response.close()


# Users
@unpacker(msgpack.unpackb)
@asynchronous
def user_exists(name, response):
    print name
    r = yield db.exists(name)
    print r
    response.write(r)
    response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def user_create(info, response):
    log.info(str(info))
    r = yield db.create(info)
    response.write(r)
    response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def user_login(info, response):
    log.info(str(info))
    name = info['name']
    password = info['password']
    r = yield db.login(name, password)
    response.write(r)
    response.close()


binds = {
    # profiles
    "profile-read": profile_read,
    "profile-list": profile_list,
    "profile-remove": profile_remove,
    # runlists
    "runlist-read": runlist_read,
    "runlist-list": runlist_list,
    # hosts
    "host-add": host_add,
    "host-list": host_list,
    "host-remove": host_remove,
    # users
    "user-exists": user_exists,
    "user-create": user_create,
    "user-login": user_login,
}

if __name__ == '__main__':
    W = Worker()
    W.run(binds)
