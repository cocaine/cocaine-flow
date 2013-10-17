"""Commits"""
import msgpack
import json

from cocaine.services import Service
from cocaine.logging import Logger
from cocaine.futures.chain import Chain
from cocaine.exceptions import ServiceError

FLOW_COMMITS = "cocaine_flow_commits"
FLOW_COMMITS_TAG = "flow_commits"

COMMIT_INDEXES = ("page", "status", "summary", "app")

Log = Logger()

storage = Service("storage")


def gen_tags(commit):
    tags = [FLOW_COMMITS_TAG]
    tags.extend(["%s@%s" % (field, commit[field]) for field
                 in COMMIT_INDEXES if field in commit.keys()])
    return tags


def unpacker(func):
    def wrapper(request, response):
        raw_data = yield request.read()
        data = msgpack.unpackb(raw_data)
        yield Chain([lambda: func(data, response)])
    return wrapper


@unpacker
def commit_store(commit, response):
    yield storage.write(FLOW_COMMITS, commit['id'], 
                        json.dumps(commit), gen_tags(commit))
    response.write("ok")
    response.close()


@unpacker
def commit_find(data, response):
    tags = gen_tags(data)
    Log.info("tags %s" % tags)
    commit_items = yield storage.find(FLOW_COMMITS, tags)
    Log.info(commit_items)
    commits = list()
    for commit in commit_items:
        try:
            item = yield storage.read(FLOW_COMMITS, commit)
            commits.append(json.loads(item))
        except ServiceError:
            pass
    response.write(sorted(commits, key=lambda x: x.get('time', 0)))
    response.close()


@unpacker
def commit_update(commit, response):
    tmp = yield storage.read(FLOW_COMMITS, commit['id'])
    commit_old = json.loads(tmp)
    commit_old.update(commit)
    yield storage.write(FLOW_COMMITS, commit_old['id'], 
                        json.dumps(commit), gen_tags(commit_old))
    response.write("ok")
    response.close()
