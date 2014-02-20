#!/usr/bin/env python

import msgpack

from cocaine.services import Service
from cocaine.asio.service import Locator
from cocaine.worker import Worker
from cocaine.asio.engine import asynchronous
from cocaine.logging import Logger
from cocaine.tools.actions import profile
from cocaine.tools.actions import runlist
from cocaine.tools.actions import group


from userdb import UserDB

ITEM_IS_ABSENT = -100

log = Logger()
storage = Service("storage")
locator = Locator()


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


# groups
@unpacker(msgpack.unpackb)
@asynchronous
def group_list(_, response):
    try:
        groups = yield group.List(storage).execute()
        response.write(groups)
    except Exception as err:
        log.error(repr(err))
        response.error(-100, "Unable to read groups")
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def group_create(name, response):
    try:
        yield group.Create(storage, name).execute()
    except Exception as err:
        log.error(repr(err))
        response.error(-100, "Unable to read groups")
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def group_read(name, response):
    try:
        gcontent = yield group.View(storage, name).execute()
        response.write(gcontent)
    except Exception as err:
        log.error(repr(err))
        response.error(-100, "Unable to read groups")
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def group_remove(name, response):
    try:
        yield group.Remove(storage, name).execute()
    except Exception as err:
        log.error(repr(err))
        response.error(-100, "Unable to read groups")
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def group_pushapp(info, response):
    log.info(str(info))
    name = info["name"]
    app = info["app"]
    weight = int(info["weight"])
    log.info(str(info))
    try:
        yield group.AddApplication(storage, name, app, weight).execute()
    except Exception as err:
        log.error(repr(err))
        response.error(-100, "Unable to push app %s" % name)
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def group_popapp(info, response):
    name = info["name"]
    app = info["app"]
    try:
        yield group.RemoveApplication(storage, name, app).execute()
    except Exception as err:
        log.error(repr(err))
        response.error(-100, "Unable to pop app")
    finally:
        response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def group_refresh(name, response):
    try:
        yield group.Refresh(locator, storage, name)
    except Exception as err:
        log.error(repr(err))
        response.error(-100, "Unable to refresh")
    finally:
        response.close()


# Users
@unpacker(msgpack.unpackb)
@asynchronous
def user_exists(name, response):
    r = yield db.exists(name)
    response.write(r)
    response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def user_signup(info, response):
    r = yield db.create(info)
    response.write(r)
    response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def user_signin(info, response):
    name = info['name']
    password = info['password']
    r = yield db.login(name, password)
    response.write(r)
    response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def user_remove(name, response):
    yield db.remove(name)
    response.close()


@unpacker(msgpack.unpackb)
@asynchronous
def user_list(_, response):
    users = yield db.users()
    response.write(users)
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
    # groups
    "group-list": group_list,
    "group-create": group_create,
    "group-read": group_read,
    "group-remove": group_remove,
    "group-pushapp": group_pushapp,
    "group-popapp": group_popapp,
    "group-refresh": group_refresh,
    # users
    "user-exists": user_exists,
    "user-signup": user_signup,
    "user-signin": user_signin,
    "user-remove": user_remove,
    "user-list": user_list,
}

API = {"Version": 1,
       "Methods": binds.keys()}


def api(request, response):
    yield request.read()
    response.write(API)
    response.close()

if __name__ == '__main__':
    W = Worker()
    W.on("API", api)
    W.run(binds)
