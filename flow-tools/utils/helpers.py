import logging
import uuid
import hmac
import json
import hashlib
from functools import partial

from flow.utils.storage import Storage

from cocaine.exceptions import ServiceError

LOGGER = logging.getLogger()


SEARCH_FIELDS = ("name", "reference", "status")


def verify_password(password, user_info):
    LOGGER.info('verify_password')
    try:
        user_uuid = user_info['uuid']
        crypt_password = user_info['password']
    except KeyError:
        LOGGER.exception("Bad user info")
    try:
        result = crypt_password == hmac.new(str(user_uuid), password,
                                            digestmod=hashlib.sha1).hexdigest()
    except TypeError:
        LOGGER.exception()
    LOGGER.info("verify result %s", result)
    return result


def search_filter(regex, data):
    import re
    LOGGER.error("REGEX %s", regex)
    RX = re.compile(regex)
    res = RX.match(data["name"])\
          or RX.match(data["reference"])\
          or RX.match(data["status"])
    return res is not None


def search_application(answer, regex):
    try:
        items = yield Storage().list_app_future()
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception:
        LOGGER.exception()
    res = []
    for item in items:
        tmp = yield Storage().read_app_future(item)
        try:
            res.append(json.loads(tmp))
        except ServiceError as err:
            LOGGER.error(str(err))
        except Exception:
            LOGGER.exception()
    answer({"apps": filter(partial(search_filter, regex), res)})


def get_user(answer, name, password=None):
    item = None
    try:
        item = yield Storage().read_user_future(name)
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.exception(str(err))

    if item is None:
        response = {"users": [{}]}
    else:
        LOGGER.warning("User %s data:  %s", name, item)
        try:
            user_info = json.loads(item)
        except ValueError:
            LOGGER.exception("Bad json")
        if password is None or not verify_password(password, user_info):
            if password is None:
                status = "OK"
            else:
                status = "fail"
            response = {"users": [{"id": "me",
                                   "username": user_info['username'],
                                   "status": status}]}
        else:
            user_info.pop('uuid', None)

            user_info['password'] = password
            response = {"users": [user_info]}
    answer(response)


def store_user(answer, username, password, **kwargs):
    try:
        yield Storage().read_user_future(username)
    except ServiceError:
        pass
    else:
        LOGGER.warning('User %s already exists. Rewrite it', username)
        # TBD: Raise error

    data = dict()
    data['username'] = username
    user_uuid = uuid.uuid4().hex
    data['uuid'] = user_uuid
    data['password'] = hmac.new(user_uuid, password,
                                digestmod=hashlib.sha1).hexdigest()
    data['ACL'] = {}
    data['status'] = "OK"
    data['id'] = username
    data.update(kwargs)
    try:
        yield Storage().write_user_furure(username, json.dumps(data))
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.exception(str(err))
    else:
        answer({'user': {'id': data['id'],
                         'ACL': data['ACL'],
                         'status': data['status'],
                         'username': data['username']}})
