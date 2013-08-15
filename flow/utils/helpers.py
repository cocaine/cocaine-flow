
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
    try:
        app_info.update(data)
        yield Storage().write_app_future(data['name'], json.dumps(app_info))
    except ServiceError as err:
        LOGGER.error(err)
    answer({"app": data})


def delete_application(answer, data):
    name = data['id']
    LOGGER.error("Remove %s", name)
    try:
        LOGGER.info('Removing application info')
        yield Storage().delete_app_future(name)
    except ServiceError as err:
        LOGGER.error(str(err))
    else:
        LOGGER.info('Delete application info succesfully')

    try:
        LOGGER.info('Removing application data')
        yield Storage().delete_app_data_future(name)
    except ServiceError as err:
        LOGGER.error(str(err))
    else:
        LOGGER.info('Delete application info succesfully')

    try:
        LOGGER.info("Find commits")
        items = yield Storage().find_commit_future(exttags={"app": name})
        LOGGER.debug("FIND %d, %s", len(items), str(items))
    except ServiceError as err:
        LOGGER.error(str(err))

    LOGGER.info('Delete commits')
    for item in items:
        try:
            LOGGER.debug("Delete commit %s", item)
            yield Storage().delete_commit_future(item)
        except Exception as err:
            LOGGER.error(err)
    answer({"apps": [name]})


def deploy_application(answer, name):
    try:
        tmp = yield Storage().read_app_data_future(name)
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.error(str(err))
    else:
        print tmp


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
    answer({'commits': sorted(res, key=lambda x: x.get('time', 0))})


def get_summary(answer, summaryname):
    LOGGER.debug("Get summary")
    try:
        item = yield Storage().read_summary_future(summaryname)
    except ServiceError:
        LOGGER.exception("AAAA")
    except Exception:
        LOGGER.exception()
    res = json.loads(item)

    LOGGER.debug("Find commits")
    try:
        exttags = {"summary": summaryname, "page": 1}
        commit_items = yield Storage().find_commit_future(exttags=exttags)
        LOGGER.error(str(commit_items))
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.error(str(err))

    LOGGER.debug("Read commits")
    commits = list()
    for commit in commit_items:
        try:
            item = yield Storage().read_commit_future(commit)
            commits.append(json.loads(item))
        except ServiceError as err:
            LOGGER.error(str(err))

    answer({'summary': res, 'commits': sorted(commits,
                                              key=lambda x: x.get('time', 0))})


def update_summary(answer, data):
    try:
        tmp = yield Storage().read_summary_future(data['id'])
        summary_info = json.loads(tmp)
    except ServiceError as err:
        LOGGER.error(str(err))
    LOGGER.error("OLD %s", str(summary_info))
    LOGGER.error("UPDATE %s", str(data))
    try:
        summary_info.update(data)
        LOGGER.error("END %s", summary_info)
        yield Storage().write_summary_future(data['id'],
                                             json.dumps(summary_info))
    except ServiceError as err:
        LOGGER.error(err)
    answer({"summary": summary_info})


def find_commits(answer, **indexes):
    LOGGER.debug("Find commits")
    try:
        exttags = dict()
        exttags.update(indexes)
        commit_items = yield Storage().find_commit_future(exttags=exttags)
        LOGGER.error(str(commit_items))
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.error(str(err))

    LOGGER.debug("Read commits")
    commits = list()
    for commit in commit_items:
        try:
            item = yield Storage().read_commit_future(commit)
            commits.append(json.loads(item))
        except ServiceError as err:
            LOGGER.error(str(err))
    answer({'commits': sorted(commits, key=lambda x: x.get('time', 0))})


# def store_commit(answer, commitname, data, indexes):
#     try:
#         yield Storage().write_commit_future(commitname,
#                                             json.dumps(data),
#                                             exttags=indexes)
#     except Exception as err:
#         LOGGER.error(str(data))
#         LOGGER.error(str(err))
#     answer({'commits': [data]})


def update_commit(answer, commit):
    LOGGER.error(str(commit))
    try:
        tmp = yield Storage().read_commit_future(commit['id'])
        commit_info = json.loads(tmp)
    except ServiceError as err:
        LOGGER.error(str(err))

    try:
        commit_info.update(commit)
        indexes = {"page": commit_info['page'],
                   "app": commit_info['app'],
                   "last": commit_info['last'],
                   "status": commit_info['status'],
                   "summary": commit_info['summary']}
        yield Storage().write_commit_future(commit_info['id'],
                                            json.dumps(commit_info),
                                            exttags=indexes)
    except ServiceError as err:
        LOGGER.error(err)
    commit_info.pop('app')
    answer({"commit": commit_info})
