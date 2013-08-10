
import logging
import uuid
import hmac
import json
import hashlib

from flow.utils.storage import Storage
from flow.utils.vcs import get_vcs

from cocaine.exceptions import ServiceError

LOGGER = logging.getLogger()


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


def get_applications(answer):
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
    answer({"apps": res})


def update_application(answer, data):
    try:
        tmp = yield Storage().read_app_future(data['name'])
        app_info = json.loads(tmp)
    except ServiceError as err:
        LOGGER.error(str(err))
    LOGGER.info(str(app_info))
    try:
        app_info.update(data)
        yield Storage().write_app_future(data['name'], json.dumps(data))
    except ServiceError as err:
        LOGGER.error(err)
    answer(data)


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
            response = {"users": [{"id": user_info['id'],
                                   "username": user_info['username'],
                                   "status": status}]}
        else:
            user_info.pop('uuid', None)
            user_info.pop('password', None)
            response = {"users": [user_info]}
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


def store_profile(answer, name, data):
    try:
        data['id'] = name
        yield Storage().write_profile_future(name, json.dumps(data))
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.exception(err)
    else:
        answer({"profile": data})


def get_profile(answer, name):
    profile = None
    try:
        profile = yield Storage().read_profile_future(name)
    except ServiceError as err:
        LOGGER.error(str(err))
        answer({"profile": {}})
    except Exception:
        LOGGER.exception(err)
    else:
        answer({"profile": json.loads(profile)})


def delete_profile(answer, name):
    try:
        yield Storage().delete_profile_future(name)
    except ServiceError as err:
        LOGGER.error(str(err))
    else:
        answer({})


def list_profiles(answer):
    try:
        items = yield Storage().list_profile_future()
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception:
        LOGGER.exception()
    res = []
    for item in items:
        tmp = yield Storage().read_profile_future(item)
        try:
            res.append(json.loads(tmp))
        except ServiceError as err:
            LOGGER.error(str(err))
        except Exception:
            LOGGER.exception()
    answer({"profiles": res})


def vcs_clone(answer, repository_info):
    vcs_object = get_vcs(answer, repository_info)
    vcs_object.run()


def get_commits(answer, appname=None):
    try:
        items = yield Storage().list_commit_future(appname)
    except ServiceError as err:
        LOGGER.exception()
    except Exception:
        LOGGER.exception()
    res = []
    for item in items:
        tmp = yield Storage().read_commit_future(item)
        try:
            res.append(json.loads(tmp))
        except ServiceError as err:
            LOGGER.error(str(err))
        except Exception:
            LOGGER.exception()
    answer({'commits': res})


def get_summary(answer, summaryname):
    try:
        item = yield Storage().read_summary_future(summaryname)
    except ServiceError:
        LOGGER.exception()
    except Exception:
        LOGGER.exception()
    res = json.loads(item)
    try:
        item = yield Storage().read_commit_future(summaryname)
    except ServiceError:
        LOGGER.exception()
    except Exception:
        LOGGER.exception()
    commits = json.loads(item)
    answer({'summary': res, 'commits': [item for item in commits
                                        if item.get('page') == 1]})


def get_commits_from_page(answer, summaryname, page):
    try:
        tmp = yield Storage().read_summary_future(summaryname)
        summary = json.loads(tmp)
    except ServiceError:
        LOGGER.exception()
    app_name = summary['app']
    try:
        items = yield Storage().list_commit_future(app_name)
    except ServiceError:
        LOGGER.exception()
    res = []
    for item in items:
        tmp = yield Storage().read_commit_future(item)
        try:
            res.extend(json.loads(tmp))
        except ServiceError as err:
            LOGGER.error(str(err))
        except Exception as err:
            print err
            LOGGER.exception()
    answer({'commits': [item for item in res
                        if item.get('page') == page]})
