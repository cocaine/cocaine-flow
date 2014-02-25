import uuid
import hashlib

from Crypto.Hash import HMAC
import msgpack


# from cocaine.tools.actions.app import DockerUpload
# from cocaine.futures.chain import concurrent
from cocaine.asio.engine import asynchronous
from cocaine.logging import Logger

namespace_prefix = "flow-users@"
USER_TAG = ["FLOW_USER"]


encoder = msgpack.packb
decoder = msgpack.unpackb


class SecureStorage(object):
    def __init__(self, storage):
        self.storage = storage

    @asynchronous
    def write(self, namespace, key, blob, tags):
        yield self.storage.write(namespace, key, encoder(blob), tags)

    @asynchronous
    def read(self, namespace, key):
        res = yield self.storage.read(namespace, key)
        yield decoder(res)

    @asynchronous
    def find(self, namespace, tags):
        yield self.storage.find(namespace, tags)

    @asynchronous
    def remove(self, namespace, key):
        yield self.storage.remove(namespace, key)

    def raw_storage(self):
        return self.storage


class UserDB(object):
    def __init__(self, storage, key, namespace):
        self.storage = SecureStorage(storage)
        self.key = key
        self.logger = Logger()
        self.namespace = namespace_prefix + namespace
        self.dbnamespace = namespace_prefix + "apps"
        self.logger.info("UserDB has been initialized. Use namespace %s"
                         % self.namespace)

    @asynchronous
    def exists(self, name):
        try:
            yield self.storage.read(self.namespace, name)
        except Exception as err:
            self.logger.error(str(err))
            yield False
        else:
            yield True

    @asynchronous
    def get(self, name):
        yield self.storage.read(self.namespace, name)

    @asynchronous
    def create(self, info):
        user_info = dict()
        uid = uuid.uuid4().hex
        name = info['name']
        password = info['password']

        exists = yield self.exists(name)
        if exists:
            raise Exception("Already exists")
        # Store user uid
        user_info['uid'] = uid
        # Store username
        user_info['name'] = name
        # Crypt user passwd
        h = HMAC.new(uid)
        h.update(password)
        user_info['hash'] = h.hexdigest()
        try:
            yield self.storage.write(self.namespace, name, user_info, USER_TAG)
        except Exception as err:
            self.logger.error(str(err))
            yield False
        else:
            yield True

    @asynchronous
    def remove(self, name):
        yield self.storage.remove(self.namespace, name)

    @asynchronous
    def login(self, name, password):
        user_info = yield self.get(name)
        self.logger.info(str(user_info))
        h = HMAC.new(user_info['uid'])
        h.update(password)
        self.logger.error("%s %s" % (h.hexdigest(), user_info['hash']))
        if (h.hexdigest() == user_info['hash']):
            user_info.pop('uid')
            yield user_info
        else:
            raise Exception("Invalid pair of login/password")

    @asynchronous
    def users(self):
        yield self.storage.find(self.namespace, USER_TAG)

    @asynchronous
    def upload_app(self, user, name, path):
        self.logger.error("%s %s %s" % (user, name, path))
        yield self.write_app_info(user, name)

    @asynchronous
    def write_app_info(self, user, name):
        while True:
            info = None
            summ = ""
            try:
                info = yield self.storage.read(self.dbnamespace, user)
                summ = hashlib.md5(info).hexdigest()
            except Exception as err:
                self.logger.error(repr(err))

            apps = list()
            if info is None:
                apps = list()
            else:
                apps = msgpack.unpackb(info)

            if name in apps:
                self.logger.error("App %s has already existed" % name)
                break
            apps.append(name)

            try:
                info = yield self.storage.read(self.dbnamespace, user)
            except Exception as err:
                self.logger.error(repr(err))

            if info is not None and summ != hashlib.md5(info).hexdigest():
                self.logger.info("MD5 mismatchs. Continue")
                continue

            self.logger.info("MD5 is still valid. Do write")
            yield self.storage.write(self.dbnamespace,
                                     user,
                                     msgpack.packb(apps),
                                     USER_TAG)
            break
