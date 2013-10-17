"""All app operations"""
import json
import shutil
import tempfile
from functools import partial

import msgpack
import sh

from cocaine.services import Service
from cocaine.logging import Logger
from cocaine.exceptions import ServiceError

FLOW_APPS_DATA = "cocaine_flow_apps_data"
FLOW_APPS_DATA_TAG = "flow_apps_data"

FLOW_APPS = "cocaine_flow_apps"
FLOW_APPS_TAG = "apps"

FLOW_COMMITS = "cocaine_flow_commits"
FLOW_COMMITS_TAG = "flow_commits"

FLOW_SUMMARIES = "cocaine_flow_summaries"
FLOW_SUMMARIES_TAG = "flow_summaries"

COMMITS_PER_PAGE = 4

storage = Service("storage")
LOGGER = Logger()

COMMIT_INDEXES = ("page", "status", "summary", "app")


git = sh.git


def get_applications_info(request, response):
    yield request.read()
    items = yield storage.find(FLOW_APPS, [FLOW_APPS_TAG])
    res = []
    for item in items:
        tmp = yield storage.read(FLOW_APPS, item)
        try:
            res.append(json.loads(tmp))
        except ServiceError as err:
            LOGGER.error(str(err))
    response.write(res)
    response.close()


def update_application_info(request, response):
    raw_data = yield request.read()
    data = msgpack.unpackb(raw_data)
    tmp = yield storage.read(FLOW_APPS, data['id'])
    app_info = json.loads(tmp)
    app_info.update(data)
    yield storage.write(FLOW_APPS, app_info['id'],
                        json.dumps(app_info), [FLOW_APPS_TAG])
    response.write(data)
    response.close()


def info(percentage, message):
    return {"percentage": percentage, "message": message}


def error(percentage, message):
    return {"percentage": percentage, "fail": message}


def extract_commits(app, raw_data):
    hash_, author, timestamp, subject = raw_data.strip("\"").split("@@")
    return {'id': hash_,
            'hash': hash_,
            'message': subject,
            'status': "unactive",
            "app": app,
            'date': int(timestamp.partition(' ')[0])*1000,
            'author': author}


def upload_application(request, response):
    '''
    1. Git clone
    2. Git checkout
    3. Extract commits
    4. Pack tar.gz
    5. Store tar.gz
    6. Store commits
    7. Store summary
    8. Store app info
    '''
    raw_data = yield request.read()
    repo_info = msgpack.unpackb(raw_data)
    url = repo_info['repository']
    ref = repo_info.get('reference', '').strip() or 'HEAD'

    app_name = url.rpartition('/')[2]
    if app_name.endswith('.git'):
        app_name = app_name[:-4]
    percentage = 0

    # Create temp folder
    clone_path = tempfile.mkdtemp()
    LOGGER.info("Create tmp dir: %s" % clone_path)
    response.write(info(percentage, "Clone %s" % url))

    LOGGER.info("Clone %s" % url)
    percentage += 20
    try:
        res = git.clone(url, clone_path, "--progress")
        ref = git('rev-parse', '--short', ref, _cwd=clone_path).strip()
        app_id = "%s_%s" % (app_name, ref)

        response.write(info(percentage, "Checkout commit %s" % ref))
        res = git.checkout(ref, _cwd=clone_path)
        res = sh.git("--no-pager", "log", "-n", "20",
                     pretty="format:\"%h@@%an <%ae>@@%ad@@%s\"",
                     date="raw", _cwd=clone_path)

        commits = map(partial(extract_commits, app_id), res.splitlines())
        commits[0]['status'] = 'checkouted'

        sh.git("archive", ref, "--worktree-attributes",
               format="tar", o="app.tar", _cwd=clone_path)
        sh.gzip("app.tar", _cwd=clone_path)
    except sh.ErrorReturnCode as err:
        LOGGER.error(str(err))
        response.write(error(percentage, str(err)))
        shutil.rmtree(clone_path, ignore_errors=True)
        raise StopIteration
    app_info = {"name": app_name,
                "id": app_id,
                "reference": ref,
                "summary": app_id,
                "status": "uploaded",
                "profile": "default",
                "status-message": "normal"}

    pages = (len(commits) + 0.5 * COMMITS_PER_PAGE) / COMMITS_PER_PAGE
    summary = {"id": app_id,
               "app": app_id,
               "commits": [item.get('id') for item in commits],
               "commit": ref,
               "pages": pages,
               "repository": url,
               "developers": "",
               "dependencies": "",
               "use-frequency": "often"}

    # Store data
    response.write(info(percentage, "Store application data"))
    with open(clone_path + "/app.tar.gz", 'rb') as binary:
        yield storage.write(FLOW_APPS_DATA, app_id,
                            binary.read(), [FLOW_APPS_DATA_TAG])

    # Store summary
    response.write(info(percentage, "Store application summary"))
    yield storage.write(FLOW_SUMMARIES, app_id,
                        json.dumps(summary), [FLOW_SUMMARIES_TAG])

    # Store commits
    response.write(info(percentage, "Store application commits"))
    for i, commit in enumerate(commits):
        commit['page'] = i / COMMITS_PER_PAGE + 1
        LOGGER.error(commit['page'])
        commit['summary'] = app_id
        yield Service("flow-commit").enqueue("store_commit",
                                             msgpack.packb(commit))

    # Store app info
    response.write(info(percentage, "Store application info"))
    yield storage.write(FLOW_APPS, app_id,
                        json.dumps(app_info), [FLOW_APPS_TAG])

    # Some cleaning
    response.close()
    shutil.rmtree(clone_path, ignore_errors=True)


def destroy(request, response):
    raw_data = yield request.read()
    data = msgpack.unpackb(raw_data)
    name = data['id']
    LOGGER.debug('Removing application info')
    yield storage.remove(FLOW_APPS, name)
    LOGGER.debug('Delete application info succesfully')

    LOGGER.debug('Removing application data')
    yield storage.remove(FLOW_APPS_DATA, name)
    LOGGER.debug('Delete application data succesfully')

    LOGGER.debug("Find commits")
    items = yield storage.find(FLOW_COMMITS, ["app@" + name, FLOW_COMMITS_TAG])

    LOGGER.debug('Delete commits')
    for item in items:
        yield storage.remove(FLOW_COMMITS, item)
    response.write(name)
    response.close()
