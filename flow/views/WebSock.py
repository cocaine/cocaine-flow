import logging
import json
from functools import partial

from tornadio2 import SocketConnection
from tornadio2 import TornadioRouter
from tornadio2 import event


from flow.utils.storage import Storage
from flow.utils import helpers

from cocaine.futures.chain import Chain

APP_LOGGER = logging.getLogger()


class WebSockInterface(SocketConnection):

    def __init__(self, *args, **kwargs):
        super(WebSockInterface, self).__init__(*args, **kwargs)
        self.connection_info = None

    def on_open(self, info):
        APP_LOGGER.warning('Client connected')
        self.connection_info = info

    def on_close(self):
        APP_LOGGER.warning('Client disconnected')

    @event('logout')
    def logout(self):
        APP_LOGGER.warning('There is no handler for LOGOUT')

    @event('id:user')
    def id_user(self, data, key):
        ''' Analog of user/me '''
        # Check cookies here
        print self.connection_info  # Extract cookie!
        user = False
        if not user:
            self.emit(key,
                      {"user": {
                      "id": "me",
                      "username": "arkel",
                      "status": "OK",
                      "ACL": {}
                      }})
        else:
            self.emit(key, {"user": {"id": "me"}})
        return

    @event('create:user')
    def create_user(self, data, key):
        '''
        Create user with information in data.

        :param data: JSON contains userinfo as value for 'user' key
        :param key: name of emitted event to answer
        '''
        try:
            user_info = data['user']
            username = user_info['username']
            password = user_info['password']
            name = user_info['name']
        except KeyError as err:
            APP_LOGGER.error("Missing argument, %s", str(err))
            return

        APP_LOGGER.info('Create user: %s', username)
        APP_LOGGER.warning("event: user, method: post, key: %s", key)
        Chain([partial(helpers.store_user,
                       partial(self.emit, key),
                       username,
                       password, name=name)])

    @event('find:users')
    def find_users(self, data, key):
        '''
        Return information about the user.
        If the request is passed password and it is valid,
        it returns the full information about the user,
        otherwise just login. Is used to check whether the
        user when creating and validating passwords.

        :param data: user data as JSON
        :param key: name of emitted event to answer
        '''
        user = data['username']
        password = data.get('password')
        APP_LOGGER.debug('Read user %s, key %s', user, key)
        Chain([partial(helpers.get_user,
                       partial(self.emit, str(key)),
                       user, password)])

    @event('all:apps')
    def all_apps(self, _, key):
        '''
        Return all contained applications from the storage.

        :param _: unusable
        :param key: name of emitted event to answer
        '''
        Chain([partial(helpers.get_applications,
                       partial(self.emit, key))])

    @event('id:app')
    def id_app(self, name, key):
        APP_LOGGER.error('Mock id_app')

        def wr(obj):
            try:
                data = yield Storage().read_app_future(name)
                obj.emit(key, {"app": json.loads(data), "commits": {
                        "id": 1,
                        "summary": 1,
                        "app": name,
                        "page": 1,
                        "hash": "c43733",
                        "link": "https://github.com/...",
                        "date": 1368486236487,
                        "message": "TTTT",
                        "author": "Oleg <markelog@gmail.com>",
                        "active": True,
                        "last": False
                }})
            except Exception as err:
                print err
        Chain([partial(wr, self)])

    @event('cancel-upload')
    def cancel_upload(self, *args):
        APP_LOGGER.error('Not implemented cancel-upload')

    @event('id:profile')
    def id_profile(self, name, key):
        '''
        Return the contents of the requested profile

        :param name: profile's name
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.info("Get profile")
        Chain([partial(helpers.get_profile,
                       partial(self.emit, key),
                       name)])

    @event('create:profile')
    def create_profile(self, data, key):
        '''
        Store profile in the storage.

        :param name: JSON, which contains profile body as value
        for key 'profile'
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.info("Store profile")
        profile = data['profile']
        Chain([partial(helpers.store_profile,
                       partial(self.emit, key),
                       profile['name'],
                       profile)])

    @event('update:profile')
    def update_profile(self, profile, key):
        '''
        Update profile in the storage.

        :param name: body of profile as JSON
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.info("Put profile")
        Chain([partial(helpers.store_profile,
                       partial(self.emit, key),
                       profile['name'],
                       profile)])

    @event('delete:profile')
    def delete_profile(self, profile, key):
        '''
        Remove profile from the storage.

        :param name: body of profile as JSON
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.warning('Call delete:profile')
        name = profile['name']
        Chain([partial(helpers.delete_profile,
                       partial(self.emit, key),
                       name)])

    @event('all:profiles')
    def all_profiles(self, _, key):
        '''
        Return all contained profiles from the storage.

        :param _: unusable
        :param key: name of emitted event to answer
        '''
        Chain([partial(helpers.list_profiles,
                       partial(self.emit, key))])

    @event('all:clusters')
    def all_clusters(self, _, key):
        APP_LOGGER.error('Mock all:clusters')
        self.emit(key, {"clusters": [{"id": 1}]})

    @event('upload:app')
    def upload(self, data, key):
        '''
        Fetch application from VCS

        :param data: information about repository
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.error(str(data))
        repository_info = dict((item['name'], item['value']) for item in data)
        Chain([partial(helpers.git_clone,
                       partial(self.emit, key),
                       repository_info)])

    @event('summary')
    def summary(self, method, app_id):
        APP_LOGGER.error("Event summary, method %s, app_id %s" % (method, app_id))
        self.emit("summary/%s" % app_id, {"summary": {
                    "id": 1,
                    "app": 1,
                    "commits": [1, 2],
                    "repository": "git://github.yandex-team.ru/user/application.git",
                    "address": "test",
                    "developers": "admin, tester",
                    "tracker": "some tracker",
                    "dependencies": "sh==1.02, msgpack-python",
                    "use-frequency": "often"},
                    "commits": {
                            "id": 1,
                            "summary": 1,
                            "app": app_id,
                            "page": 1,
                            "hash": "c43733",
                            "link": "https://github.com/...",
                            "date": 1368486236487,
                            "message": "TTTT",
                            "author": "Oleg <markelog@gmail.com>",
                            "active": True,
                            "last": False
                    }})

    @event('commits')
    def commits(self, method, args, *t, **kwargs):
        print args
        #print kwargs
        self.emit(r"commits/%s" % (args['meta']['query']),
                 {"commits": [{"id": 2,
                               "summary": args['summary'],
                               "app": "MY_APP_IDe15e216fc1c639f787b1231ecdfa1bf8",
                               "page": 2,
                               "hash": "a044a3",
                               "link": "https://github.com/...",
                               "date": 1366630011651,
                               "message": "message",
                               "author": "Oleg <markelog@gmail.com>",
                               "active": False,
                               "last": True}]})

# Create TornadIO2 router
Router = TornadioRouter(WebSockInterface)
