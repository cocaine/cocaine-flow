#
#    Copyright (c) 2011-2013 Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2013 Other contributors as noted in the AUTHORS file.
#
#    This file is part of Cocaine.
#
#    Cocaine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    Cocaine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import logging
import uuid
from functools import partial

import msgpack
from tornadio2 import SocketConnection
from tornadio2 import TornadioRouter
from tornadio2 import event

from flow.utils import helpers

from cocaine.services import Service
from cocaine.exceptions import ChokeEvent
from cocaine.futures.chain import Chain
from cocaine.futures.chain import source

APP_LOGGER = logging.getLogger()


class WebSockInterface(SocketConnection):

    def __init__(self, *args, **kwargs):
        super(WebSockInterface, self).__init__(*args, **kwargs)
        self.connection_info = None
        self._cookie = False
        self.vcs_objects = dict()

    def on_open(self, info):
        APP_LOGGER.warning('Client connected')
        self.connection_info = info
        self._cookie = info.get_cookie("user") or False
        APP_LOGGER.info("%s", info.cookies)
        APP_LOGGER.error(self._cookie)

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
        if True:  # self._cookie:
            APP_LOGGER.info('Find cookies')
            self.emit(key,
                      {"user": {
                       "id": "me",
                       "username": "arkel",
                       "status": "OK",
                       "ACL": {},
                       "name": "TEST"}})
        else:
            APP_LOGGER.info("Give me cookies, I'm hungry")
            self.emit(key, {"user": {"id": "me", "status": "fail"}})

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
        APP_LOGGER.error(str(data))
        user = data['username']
        password = data.get('password')
        APP_LOGGER.debug('Read user %s, key %s', user, key)
        if password is None:
            Chain([partial(helpers.get_user,
                           partial(self.emit, str(key)),
                           user, password)])
        else:
            Chain([partial(helpers.get_user,
                           partial(self.set_cookie, str(key)),
                           user, password)])

    @event('all:apps')
    @source
    def all_apps(self, _, key):
        '''
        Return all contained applications from the storage.

        :param _: unusable
        :param key: name of emitted event to answer
        '''
        res = yield Service("flow-app").enqueue("get", "")
        self.emit(key, {"apps": res})

    @event('id:profile')
    @source
    def id_profile(self, name, key):
        '''
        Return the contents of the requested profile

        :param name: profile's name
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.info("Get profile")
        res = yield Service("flow-profile").enqueue("get", name)
        print res
        self.emit(key, {"profile": res})

    @event('create:profile')
    @source
    def create_profile(self, data, key):
        '''
        Store profile in the storage.

        :param name: JSON, which contains profile body as value
        for key 'profile'
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.info("Store profile")
        profile = data['profile']
        task = msgpack.packb([profile['name'], profile])
        res = yield Service("flow-profile").enqueue("store", task)
        self.emit(key, res)

    @event('update:profile')
    @source
    def update_profile(self, profile, key):
        '''
        Update profile in the storage.

        :param name: body of profile as JSON
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.info("Put profile")
        task = msgpack.packb([profile['name'], profile])
        res = yield Service("flow-profile").enqueue("store", task)
        self.emit(key, res)

    @event('delete:profile')
    @source
    def delete_profile(self, profile, key):
        '''
        Remove profile from the storage.

        :param name: body of profile as JSON
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.warning('Call delete:profile')
        res = yield Service("flow-profile").enqueue("delete", profile['name'])
        self.emit(key, res)

    @event('all:profiles')
    @source
    def all_profiles(self, _, key):
        '''
        Return all contained profiles from the storage.

        :param _: unusable
        :param key: name of emitted event to answer
        '''
        res = yield Service("flow-profile").enqueue("all", "")
        self.emit(key, {"profiles": res})

    # @event('all:clusters')
    # def all_clusters(self, _, key):
    #     APP_LOGGER.error('Mock all:clusters')
    #     self.emit(key, {"clusters": [{"id": 1}]})

    @event('upload:app')
    @source
    def upload(self, data, key, *args):
        '''
        Fetch application from VCS

        :param data: information about repository
        :param key: name of emitted event to answer
        '''
        APP_LOGGER.error("UPLOAD APP")
        upload_id = uuid.uuid4()
        message = "Start uploading"
        self.emit(key, {"message": message,
                        "percentage": 0,
                        "uploadId": upload_id.hex})

        repo_info = dict((item['name'], item['value']) for item in data)

        i = yield Service("flow-app").enqueue("upload",
                                              msgpack.packb(repo_info))
        message = '\n'.join((message, i.get('message') or i.get('fail')))
        try:
            while True:
                i = yield
                message = '\n'.join((message, i.get('message')
                                     or i.get('fail')))
                i['message'] = message
                self.emit(key, i)
        except ChokeEvent:
            pass

        self.emit(key, {"finished": True,
                        "message": message + '\nDone',
                        "percentage": 100})

    @event('update:app')
    @source
    def update_app(self, data, key):
        '''
        Update fields of app structure
        '''
        APP_LOGGER.error(str(data))
        res = yield Service("flow-app").enqueue("update", msgpack.packb(data))
        print res
        self.emit(key, {"app": data})

    @event('delete:app')
    @source
    def delete_app(self, data, key):
        '''
        Delete all information about application
        '''
        APP_LOGGER.error("delete:app")
        res = yield Service("flow-app").enqueue("destroy", msgpack.packb(data))
        print res
        self.emit(key, {"apps": [res]})

    @event('deploy:app')
    @source
    def deploy_app(self, app_id):
        '''
        Deploy application to the cloud

        :param data: application name
        :param key: name of emitted event to answer
        '''
        print(app_id)
        key = "keepalive:app/%s" % app_id
        logs = "Deploy"
        # Chain([partial(helpers.deploy_application,
        #                self.emit,
        #                app_id)])
        msg = yield Service("flow-app").enqueue("deploy", app_id)
        print msg
        try:
            while True:
                msg = yield
                print msg
                msg['status'] = "deploy"
                self.emit(key, msg)
        except ChokeEvent:
            pass
        self.emit(key, {"app": {"status": "normal", "id": app_id}})
        # {'percentage': 0, 'id': 'flask-cocaine-pycon_3a424b3', 'logs': 'Deploing'}

    # @event("refresh:app")
    # def refresh_app(self, app_id):
    #     APP_LOGGER.info("refresh:app")
    #     Chain([partial(helpers.refresh_application,
    #                    self.emit, app_id)])

    @event("search:apps")
    def search_apps(self, query, key):
        Chain([partial(helpers.search_application,
                       partial(self.emit, key),
                       query)])

    # @event("cancel:update")
    # def cancel_update(self, app_id):
    #     APP_LOGGER.error("CANCEL UPDATE")
    #     key = "keepalive:app/%s" % app_id
    #     self.emit(key,  {"app": {"id": app_id,
    #                              "status": "normal",
    #                              "logs": None,
    #                              "percentage": None,
    #                              "action": None}})

    # @event('cancel:deploy')
    # def cancel_deploy(self, app_id):
    #     APP_LOGGER.info("Cancel deploy")
    #     key = "keepalive:app/%s" % app_id
    #     self.emit(key,  {"app": {"id": app_id,
    #                              "status": "uploaded",
    #                              "logs": None,
    #                              "percentage": None,
    #                              "action": None}})

    @event('id:summary')
    @source
    def id_summary(self, name, key):
        '''
        Get summary and commits with name 'name'
        '''
        APP_LOGGER.error('id:summary %s', name)
        s = Service('flow-commit')
        summary = yield s.enqueue('get_summary', name)
        tags = msgpack.packb({"page": 1, "summary": name})
        commits = yield s.enqueue('find_commit', tags)
        self.emit(key, {"summary": summary, "commits": commits})

    @event('update:summary')
    @source
    def update_summary(self, data, key):
        '''
        Update summary structure
        '''
        APP_LOGGER.error("Update summary")
        task = msgpack.packb(data)
        res = yield Service('flow-commit').enqueue('update_summary', task)
        self.emit(key, {"summary": res})

    @event('find:commits')
    @source
    def find_commits(self, data, key):
        """ engine.asynch """
        APP_LOGGER.error('find:commits')
        res = yield Service("flow-commit").enqueue("find_commit",
                                                   msgpack.packb(data))
        print res
        self.emit(key, {'commits': res})

    @event('update:commit')
    @source
    def update_commit(self, commit, key):
        """ Update fields of commit structure """
        APP_LOGGER.error('update:commit')
        res = yield Service("flow-commit").enqueue("update_commit",
                                                   msgpack.packb(commit))
        print res
        self.emit(key, {'commit': res})

    # @event('cancel:upload')
    # def cancel_upload(self, upload_id):
    #     APP_LOGGER.error("CANCELED %s", str(upload_id))
    #     vcs_object = self.vcs_objects.get(upload_id, None)
    #     if vcs_object is not None:
    #         vcs_object.cancel()
    #     self.emit("Cancel")

    #util
    def set_cookie(self, key, data):
        status = "fail"
        try:
            status = data['users'][0]['status']
        except KeyError:
            APP_LOGGER.error('Missing key')
        except Exception:
            APP_LOGGER.exception()
        if status == "OK":
            APP_LOGGER.info("Sign in succesfully")
            self._cookie = True
        else:
            APP_LOGGER.error("Sign in fail")
        self.emit(key, data)

    # def store_uploader(self, upload_id, vcs_object):
    #     APP_LOGGER.info("Register vcs object %s for id %s",
    #                     vcs_object, upload_id)
    #     self.vcs_objects[upload_id] = vcs_object

# Create TornadIO2 router
Router = TornadioRouter(WebSockInterface, namespace="flow/api/socket.io")
