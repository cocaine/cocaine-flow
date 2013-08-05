import json
import logging
import uuid
import hmac
import shutil
import hashlib
from functools import partial


from flow.utils.asyncprocess import asyncprocess
from flow.utils.storage import Storage

from cocaine.futures.chain import Chain
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
        answer({"profile": {"id": name}})


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

VCS_TEMP_DIR = "/tmp/COCAINE_FLOW"


def git_clone(answer, repository_info):
    repo_url = repository_info['repository']
    LOGGER.info("Clone GIT repository  %s", repo_url)
    if repository_info['reference'] == '':
        repository_info['reference'] = 'HEAD'

    LOGGER.info("Ref:  %s", repository_info['reference'])
    answer({"message": "Clone repository", "percentage": 0})
    try:
        LOGGER.info('Clean temp folder %s', VCS_TEMP_DIR)
        shutil.rmtree(VCS_TEMP_DIR)
    except OSError as err:
        LOGGER.error(err)

    handle_repo_data = on_git_clone(answer, repository_info, VCS_TEMP_DIR)
    handle_repo_data.next()
    clone_command = "git clone %s %s --progress" % (repo_url,
                                                    VCS_TEMP_DIR)
    asyncprocess(clone_command, handle_repo_data.send)


def on_git_clone(answer, repository_info, path):
    """Upload from git process"""
    msg = ["Cloning %s\r\n" % repository_info['repository'], "", "", "", ""]
    while True:
        data = yield
        if data is not None:
            for line in data.split('\r'):
                if "Counting objects" in line:
                    msg[1] = line
                    prog = 25
                elif "Compressing objects" in line:
                    msg[2] = line
                    prog = 40
                elif "Receiving objects:" in line:
                    msg[3] = line
                    prog = 60
                elif "Resolving deltas:" in line:
                    msg[4] = line
                    prog = 75
                answer({"message": ''.join(msg),
                        "percentage": prog})
        else:
            break
    Chain([partial(after_git_clone, answer, msg, path, repository_info)])


def after_git_clone(answer, msg, path, repository_info):
    print "git clone finish"
    ref = repository_info.get('reference', 'HEAD')

    app_id = "MY_APP_ID" + hashlib.md5(str(ref)).hexdigest()
    app_info = {"name": app_id,
                "id": app_id,
                "reference": ref,
                "status": "OK",
                "profile": 1,
                "status-message": "normal"}

    # Make tar.gz
    msg.append("Make tar.gz\n")
    answer({"message": ''.join(msg),
            "percentage": 90})

    shutil.make_archive("%s/%s" % (path, app_id),
                        "gztar", root_dir=path,
                        base_dir=path, logger=LOGGER)

    # Store archive
    msg.append("Store archive\n")
    answer({"message": ''.join(msg),
            "percentage": 95})
    try:
        application_data = open("%s/%s.tar.gz" % (path, app_id), 'rb').read()
        yield Storage().write_app_data_future(app_id, application_data)
    except ServiceError as err:
        LOGGER.error(repr(err))
    except Exception as err:
        LOGGER.error(err)

    try:
        msg.append("Store information about application\n")
        answer({"message": ''.join(msg),
                "percentage": 98})

        yield Storage().write_app_future(app_id, json.dumps(app_info))
        msg.append("Done\n")
        answer({"finished": True,
                "id": app_id,
                "percentage": 100,
                "message": ''.join(msg)})
    except ServiceError as err:
        LOGGER.error(repr(err))
    except Exception as err:
        LOGGER.error(err)
