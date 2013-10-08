#!/usr/bin/env python
# encoding: utf-8
#
#    Copyright (c) 2011-2012 Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2011-2012 Other contributors as noted in the AUTHORS file.
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

import shutil
import logging
import hashlib
import json
import re
from os import path

import pygit2

from cocaine.futures.chain import Chain
from cocaine.futures.chain import concurrent
from cocaine.exceptions import ServiceError

from flow.utils.asyncprocess import asyncprocess
from flow.utils.storage import Storage


LOGGER = logging.getLogger()

VCS_TEMP_DIR = "/tmp/COCAINE_FLOW"

COMMITS_PER_PAGE = 4

MAX_COMMITS = 20

regex = re.compile("\[K")


def get_vcs(*args):
    return GIT(*args)


def detect_app_name(repository_info):
    url = repository_info['repository']
    _, temp_name = url.rsplit('/', 1)
    if temp_name.endswith('.git'):
        temp_name = temp_name[:-4]
    app_name = '_'.join((temp_name, repository_info['reference']))
    LOGGER.info('Detect application name %s', app_name)
    return app_name


class GIT(object):

    def __init__(self, answer, repository_info):
        self.repository_info = repository_info
        self.answer = answer
        self.msg = None
        self.repo = None
        self.app_id = None
        self.upload_id = None
        self._canceled = False
        self.on_canceled = None

    def run(self):
        Chain([self.make_it])

    def cancel(self):
        self._canceled = True

    def make_it(self):
        try:
            repo_url = self.repository_info['repository']
        except Exception as err:
            LOGGER.error(str(err))
            self.answer({"fail": "Repository key is missing",
                         "percentage": 0,
                         "message": "Code error"})
            return

        LOGGER.info("Clone GIT repository  %s", repo_url)
        if self.repository_info['reference'] == '':
            self.repository_info['reference'] = 'HEAD'

        LOGGER.info("Ref: %s", self.repository_info['reference'])
        self.answer({"message": "Clone repository", "percentage": 10})

        try:
            LOGGER.info('Clean temp folder %s', VCS_TEMP_DIR)
            shutil.rmtree(VCS_TEMP_DIR)
        except OSError as err:
            LOGGER.error(err)

        handle_repo_data = self._on_git_clone()
        handle_repo_data.next()
        clone_command = "git clone %s %s --progress" % (repo_url,
                                                        VCS_TEMP_DIR)
        ret_code = yield asyncprocess(clone_command, handle_repo_data.send)
        LOGGER.error("Check discard %s", self._canceled)
        if self._canceled:
            raise StopIteration

        LOGGER.error(ret_code)
        if ret_code != 0:
            self.answer({"fail": "BLABLA",
                         "message": "Clone repository %s %s" % (repo_url,
                                                                self.repository_info['reference']),
                         "percentage": 10})
            return

        # ====== Package.json
        def f():
            while True:
                data = yield
                self.msg.append(data)
                print data
                self.answer({"message": ''.join(self.msg),
                     "percentage": 20})

        if path.exists("%s/package.json" % VCS_TEMP_DIR):
            LOGGER.error("Find package.json")
            g = f()
            g.next()
            ret_code = yield asyncprocess("npm install", g.send, cwd=VCS_TEMP_DIR)
            if ret_code == 0:
                LOGGER.error("Ret code %d", ret_code)
                self.answer({"fail": "World had exploded, dude",
                             "message": "Clone repository %s %s" % (repo_url,
                                                                    self.repository_info['reference']),
                             "percentage": 10})
                raise StopIteration
        # ===================
        ref = self.repository_info.get('reference', 'HEAD')
        self.repo = pygit2.Repository(VCS_TEMP_DIR)

        active_commit_hex = self.repo.head.get_object().hex

        app_id = detect_app_name(self.repository_info)
        self.app_id = app_id
        LOGGER.error(app_id)
        commits = [_ for _ in self._extract_commits(active_commit_hex)]
        app_info = {"name": app_id,
                    "id": app_id,
                    "reference": ref,
                    "summary": app_id,
                    "status": "uploaded",
                    "profile": "default",
                    "status-message": "normal"}

        summary = {"id": app_id,
                   "app": app_id,
                   "commits": [item.get('id') for item in commits],
                   "commit": active_commit_hex[:7],
                   "pages": len(commits) / COMMITS_PER_PAGE,
                   "repository": repo_url,
                   "developers": "",
                   "dependencies": "",
                   "use-frequency": "often"}

        # Make tar.gz
        self.msg.append("Make tar.gz\n")
        self.answer({"message": ''.join(self.msg),
                     "percentage": 90})

        @concurrent
        def pack():
            import tarfile, os
            packagePath = os.path.join(VCS_TEMP_DIR, '%s.tar.gz' % hashlib.md5(app_id).hexdigest())
            tar = tarfile.open(packagePath, mode='w:gz')
            tar.add(VCS_TEMP_DIR, arcname='')
            tar.close()

        res = yield pack()
        print res
        LOGGER.error('OK')
        # Store archive
        LOGGER.error("SAVE")
        self.msg.append("Store archive\n")
        self.answer({"message": ''.join(self.msg),
                     "percentage": 95})

        try:
            LOGGER.debug('Save application %s data', app_id)
            application_data = open("%s/%s.tar.gz" % (VCS_TEMP_DIR,
                                                      hashlib.md5(app_id).hexdigest()),
                                    'rb').read()
            yield Storage().write_app_data_future(app_id, application_data)
        except ServiceError as err:
            LOGGER.error(repr(err))
        except Exception as err:
            LOGGER.error(err)

        LOGGER.debug('Save application %s commits', app_id)
        for commit in commits:
            try:
                commit['summary'] = app_id
                indexes = {"page": commit['page'],
                           "app": commit['app'],
                           "status": commit['status'],
                           "summary": commit['summary']}
                yield Storage().write_commit_future(commit['id'],
                                                    json.dumps(commit),
                                                    exttags=indexes)
            except ServiceError as err:
                LOGGER.error(str(err))
            except Exception as err:
                LOGGER.error(str(err))

        ###
        # ADD APPLICATION SUMMARY
        try:
            LOGGER.debug('Save application %s summary', app_id)
            yield Storage().write_summary_future(app_id,
                                                 json.dumps(summary))
        except ServiceError as err:
            LOGGER.error(str(err))
        except Exception as err:
            LOGGER.error(str(err))
        ###

        try:
            self.msg.append("Store information about application")
            self.answer({"message": ''.join(self.msg),
                         "percentage": 98})

            yield Storage().write_app_future(app_id, json.dumps(app_info))
            self.answer({"finished": True,
                         "id": app_id,
                         "percentage": 100,
                         "message": ''.join(self.msg)})
        except ServiceError as err:
            LOGGER.error(repr(err))
        except Exception as err:
            LOGGER.error(err)
        if self._canceled:
            raise Exception("CANCELED")


    def _on_git_clone(self):
        '''
        so bad
        '''
        self.msg = ["Cloning %s\r\n" % self.repository_info['repository'],
                    "", "", "", ""]
        prog = 0
        try:
            while True:
                data = yield
                if data is not None:
                    for line in data.split('\r'):
                        if "Counting objects" in line:
                            self.msg[1] = regex.sub(" ", line)
                            prog = 25
                        elif "Compressing objects" in line:
                            self.msg[2] = regex.sub(" ", line)
                            prog = 40
                        elif "Receiving objects:" in line:
                            self.msg[3] = regex.sub(" ", line)
                            prog = 60
                        elif "Resolving deltas:" in line:
                            self.msg[4] = regex.sub(" ", line)
                            prog = 75
                        self.answer({"message": ''.join(self.msg),
                                     "percentage": prog})
                else:
                    break
        except Exception as err:
            LOGGER.error(err)

    def _extract_commits(self, active_commit_hex):
        head = self.repo.head.get_object()
        for i, commit in enumerate(self.repo.walk(head.oid,
                                                  pygit2.GIT_SORT_TIME)):
            if i > MAX_COMMITS:
                break
            yield  {'id': commit.hex[:7] + self.app_id,
                    'page': i / COMMITS_PER_PAGE + 1,
                    'app': self.app_id,
                    'hash': commit.hex[:7],
                    'message': commit.message,
                    'status': 'unactive' if active_commit_hex != commit.hex else "checkouted",
                    'date': commit.commit_time * 1000,
                    'author': '%s <%s>' % (commit.author.name,
                                           commit.author.email)}
