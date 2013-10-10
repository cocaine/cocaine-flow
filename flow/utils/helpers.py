import logging
import uuid
import hmac
import json
import hashlib
import os
from functools import partial

from flow.utils.storage import Storage
from flow.utils.vcs import get_vcs

from cocaine.futures.chain import Chain
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


def get_applications(answer): #DONE
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

def search_filter(regex, data):
    import re
    LOGGER.error("REGEX %s", regex)
    RX = re.compile(regex)
    res = RX.match(data["name"]) or RX.match(data["reference"]) or RX.match(data["status"])
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


def update_application(answer, data):
    try:
        tmp = yield Storage().read_app_future(data['name'])
        app_info = json.loads(tmp)
        app_info.update(data)
        yield Storage().write_app_future(data['name'], json.dumps(app_info))
    except ServiceError as err:
        LOGGER.error(err)
    except Exception as err:
        LOGGER.error(str(err))
    else:
        answer({"app": data})

def refresh_application(answer, app_id):
    LOGGER.info("Start refresh")
    logmessage = "Start refresh"
    try:
        key = "keepalive:app/%s" % app_id
        answer(key, {"app": {"id": app_id,
                         "status": "updating",
                         "logs": logmessage,
                         "percentage": 20}})
    except Exception as err:
        print err
    import time
    time.sleep(0.5)

    try:
        tmp = yield Storage().read_app_future(app_id)
        app_info = json.loads(tmp)
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.error(str(err))

    time.sleep(0.5)
    logmessage += '\n Update app info'
    answer(key, {"app": {"id": app_id,
                         "status": "updating",
                         "logs": logmessage,
                         "percentage": 40}})

    app_info['status'] = 'normal'
    LOGGER.debug("Get summary")
    try:
        summaryname = app_info['summary']
        item = yield Storage().read_summary_future(summaryname)
    except ServiceError:
        LOGGER.exception("AAAA")
    except Exception as err:
        LOGGER.exception("AAA")
    res = json.loads(item)


    try:
        app_data = yield Storage().read_app_data_future(app_id)
    except Exception as err:
        LOGGER.error(str(err))
    else:
        # Unpack archive and deploy, and start - make it through tools
        import tarfile
        import shutil
        with open("/tmp/sample.tar.gz",'wb') as f:
            f.write(app_data)
        try:
            shutil.rmtree("./tmp/COCAINE_FLOW")
        except Exception as err:
            print err
        tar = tarfile.open("/tmp/sample.tar.gz")
        tar.extractall()
        tar.close()
    #=============================


    try:
        yield Storage().write_app_future(app_id, json.dumps(app_info))
    except ServiceError as err:
        LOGGER.error(err)
    except Exception as err:
        LOGGER.error(str(err))
    time.sleep(0.5)
    answer(key, {"app": {"id": app_id,
                         "status": "updating",
                         "logs": logmessage + "\nDONE",
                         "percentage": 100}})
    time.sleep(0.5)
    answer("keepalive:app/%s" % app_id,
           {"app": {"id": app_id,
                    "status": "normal",
                    "logs": None,
                    "percentage": 100}})

def delete_application(answer, data):
    name = data['id']
    try:
        LOGGER.debug('Removing application info')
        yield Storage().delete_app_future(name)
        LOGGER.debug('Delete application info succesfully')

        LOGGER.debug('Removing application data')
        yield Storage().delete_app_data_future(name)
        LOGGER.debug('Delete application data succesfully')

        LOGGER.debug("Find commits")
        items = yield Storage().find_commit_future(exttags={"app": name})
        LOGGER.debug("FIND %d, %s", len(items), str(items))

        LOGGER.debug('Delete commits')
        for item in items:
            LOGGER.debug("Delete commit %s", item)
            yield Storage().delete_commit_future(item)
    except ServiceError as err:
        LOGGER.error(err)
    except Exception as err:
        LOGGER.error(err)
    else:
        answer({"apps": [name]})



def deploy_application(answer, app_id):
    logmessage = "Start"
    key = "keepalive:app/%s" % app_id

    answer(key, {"app": {"id": app_id,
                         "status": "deploy",
                         "logs": logmessage,
                         "percentage": 20}})
    try:
        tmp = yield Storage().read_app_future(app_id)
        app_info = json.loads(tmp)
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        print err

    app_info['status'] = 'normal'

    LOGGER.debug("Get summary")
    try:
        item = yield Storage().read_summary_future(app_id)
    except ServiceError:
        LOGGER.exception("AAAA")
    except Exception:
        LOGGER.exception()
    res = json.loads(item)
    print res

    LOGGER.debug("Find checkouted commit")
    try:
        exttags = {"app": app_id, "status": "checkouted"}
        commit_items = yield Storage().find_commit_future(exttags=exttags)
        LOGGER.error(str(commit_items))
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.error(str(err))

    checkouted_commit_id = None
    if len(commit_items) > 0:
        checkouted_commit_id = commit_items[0]
    else:
        LOGGER.error("There is no checkouted commit")
        import time
        time.sleep(0.5)
        answer("keepalive:app/%s" % app_id,
           {"app": {"id": app_id,
                    "status": "normal",
                    "logs": "There is no checkouted commit",
                    "percentage": 100}})
        raise StopIteration
     
    LOGGER.debug("Find active commit")
    try:
        exttags = {"app": app_id, "status": "active"}
        commit_items = yield Storage().find_commit_future(exttags=exttags)
        LOGGER.error(str(commit_items))
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.error(str(err))

    active_commit_id = None
    if len(commit_items) > 0:
        active_commit_id = commit_items[0]

    try:
        item = yield Storage().read_commit_future(checkouted_commit_id)
        checkouted_commit = json.loads(item)
    except ServiceError as err:
        LOGGER.error(str(err))
    checkouted_commit['status'] = "active"
    try:
        yield Chain([lambda: update_commit(lambda x: None, checkouted_commit)])
    except Exception as err:
        print err

    active_commit = None
    if active_commit_id:
        try:
            item = yield Storage().read_commit_future(active_commit_id)
            active_commit = json.loads(item)
        except ServiceError as err:
            LOGGER.error(str(err))
        active_commit['status'] = "unactive"
        try:
            yield Chain([lambda: update_commit(lambda x: None, active_commit)])
        except Exception as err:
            print err

    #=============================
    try:
        app_data = yield Storage().read_app_data_future(app_id)
    except Exception as err:
        LOGGER.error(str(err))
    else:
        # Unpack archive and deploy, and start - make it through tools
        import tarfile
        import sh
        import shutil
        answer(key, {"app": {"id": app_id, "status": "deploy",
                             "logs": "Fetch archive", "percentage": 40}})
        with open("/tmp/%s.tar.gz" % app_id,'wb') as f:
            f.write(app_data)
        try:
            shutil.rmtree("/tmp/%s" % app_id)
        except Exception as err:
            print "shutil", err
        os.mkdir("/tmp/%s" % app_id)
        tar = tarfile.open("/tmp/%s.tar.gz" % app_id)
        tar.extractall(path="/tmp/%s" % app_id)
        tar.close()
        answer(key, {"app": {"id": app_id, "status": "deploy",
                             "logs": "Deploy application", "percentage": 60}})
        tools = sh.__getattr__("cocaine-tool")
        print "COCAINE_TOOLS", tools.app.upload("--name", app_id,
                                                "/tmp/%s" % app_id, "--timeout", "50")
        cmd = "--name %s --profile default" % app_id
        answer(key, {"app": {"id": app_id, "status": "deploy",
                             "logs": "Start application", "percentage": 80}})
        tools.app.start(cmd.split(" "))

    #=============================
    try:
        yield Chain([lambda: update_application(lambda y: None, app_info)])
    except ServiceError as err:
        print err
    except Exception as err:
        LOGGER.error(repr(err))
    answer("keepalive:app/%s" % app_id,
           {"app": {"id": app_id,
                    "status": "normal",
                    "logs": None,
                    "percentage": 100}})
    tmp = [i for i in [active_commit, checkouted_commit] if i is not None]
    if len(tmp) > 0:
        answer("keepalive:summary/%s" % app_id, 
               {"summary": {
                "id": app_id,
                "commit": None},
                "commits": tmp,
               })
    try:
        tmp = yield Storage().read_app_future(app_id)
        app_info = json.loads(tmp)
    except ServiceError as err:
        LOGGER.error(str(err))
    except Exception as err:
        LOGGER.error(str(err))

    answer("keepalive:app/%s" % app_id,
           {"app": app_info})


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


def vcs_clone(answer, register_vcs, repository_info):
    vcs_object = get_vcs(answer, repository_info)
    register_vcs(vcs_object)
    vcs_object.on_canceled = partial(delete_application, lambda x: None)
    vcs_object.run()


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
                   "status": commit_info['status'],
                   "summary": commit_info['summary']}
        yield Storage().write_commit_future(commit_info['id'],
                                            json.dumps(commit_info),
                                            exttags=indexes)
    except ServiceError as err:
        LOGGER.error(err)
    commit_info.pop('app')
    answer({"commit": commit_info})
