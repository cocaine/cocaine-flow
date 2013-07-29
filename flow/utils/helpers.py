import json
import logging
import uuid
import hmac
import hashlib

from flow.utils.storage import Storage
from cocaine.exceptions import ServiceError

logger = logging.getLogger()


def verify_password(password, user_info):
    logger.info('verify_password')
    try:
        user_uuid = user_info['uuid']
        crypt_password = user_info['password']
    except KeyError:
        logger.exception("Bad user info")
    try:
        result = crypt_password == hmac.new(str(user_uuid), password,
                                            digestmod=hashlib.sha1).hexdigest()
    except TypeError:
        logger.exception()
    logger.info("verify result %s", result)
    return result


def get_applications(answer):
    try:
        items = yield Storage().list_app_future()
    except Exception:
        logger.exception()
    res = []
    for item in items:
        tmp = yield Storage().read_app_future(item)
        try:
            res.append(json.loads(tmp))
        except Exception:
            logger.exception()
    answer({"apps": res})


def get_user(answer, name, password=None):
    item = None
    try:
        item = yield Storage().read_user_future(name)
    except ServiceError as err:
        logger.error(str(err))
    except Exception as err:
        logger.exception(str(err))
    if item is None:
        response = {"users": [{}]}
    else:
        logger.warning("User %s data:  %s", name, item)
        try:
            user_info = json.loads(item)
        except ValueError:
            logger.exception("Bad json")
        if password is None:
            response = {"users": [{"id": user_info['id'],
                                   "username": user_info['username'],
                                   "status": "OK"}]}
        elif verify_password(password, user_info):
            user_info.pop('uuid', None)
            user_info.pop('password', None)
            response = {"users": [user_info]}
            print response
    answer(response)


def store_user(answer, username, password, **kwargs):
    '''
      Create new user
      {"user": {
              "id": "me",
              "username": "arkel",
              "status": "OK",
              "ACL": {}
              }
    '''
    try:
        yield Storage().read_user_future(username)
    except ServiceError:
        pass
    else:
        logger.warning('User %s already exists. Rewrite it', username)
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
        logger.error(str(err))
    except Exception as err:
        logger.exception(str(err))
    else:
        answer({'user': {'id': data['id'],
                         'ACL': data['ACL'],
                         'status': data['status'],
                         'username': data['username']}
                })
