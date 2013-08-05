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

import pygit2

from cocaine.futures.chain import Chain
from cocaine.exceptions import ServiceError

from flow.utils.asyncprocess import asyncprocess
from flow.utils.storage import Storage


LOGGER = logging.getLogger()

VCS_TEMP_DIR = "/tmp/COCAINE_FLOW"


def get_vcs(answer, repository_info):
    return GIT(answer, repository_info)


class GIT(object):

    def __init__(self, answer, repository_info):
        self.repository_info = repository_info
        self.answer = answer
        self.msg = None
        self.repo = None

    def run(self):
        repo_url = self.repository_info['repository']
        LOGGER.info("Clone GIT repository  %s", repo_url)
        if self.repository_info['reference'] == '':
            self.repository_info['reference'] = 'HEAD'

        LOGGER.info("Ref:  %s", self.repository_info['reference'])
        self.answer({"message": "Clone repository", "percentage": 0})
        try:
            LOGGER.info('Clean temp folder %s', VCS_TEMP_DIR)
            shutil.rmtree(VCS_TEMP_DIR)
        except OSError as err:
            LOGGER.error(err)

        handle_repo_data = self._on_git_clone()
        handle_repo_data.next()
        clone_command = "git clone %s %s --progress" % (repo_url,
                                                        VCS_TEMP_DIR)
        asyncprocess(clone_command, handle_repo_data.send)

    def _on_git_clone(self):
        '''
        so bad
        '''
        self.msg = ["Cloning %s\r\n" % self.repository_info['repository'],
                    "", "", "", ""]
        while True:
            data = yield
            if data is not None:
                for line in data.split('\r'):
                    if "Counting objects" in line:
                        self.msg[1] = line
                        prog = 25
                    elif "Compressing objects" in line:
                        self.msg[2] = line
                        prog = 40
                    elif "Receiving objects:" in line:
                        self.msg[3] = line
                        prog = 60
                    elif "Resolving deltas:" in line:
                        self.msg[4] = line
                        prog = 75
                    self.answer({"message": ''.join(self.msg),
                                 "percentage": prog})
            else:
                break
        Chain([self._after_git_clone])

    def _after_git_clone(self):
        ref = self.repository_info.get('reference', 'HEAD')
        self.repo = pygit2.Repository(VCS_TEMP_DIR)
        print self.repo
        get_commits = self._extract_commits()
        for i in get_commits:
            LOGGER.info(i)

        app_id = "MY_APP_ID" + hashlib.md5(str(ref)).hexdigest()
        app_info = {"name": app_id,
                    "id": app_id,
                    "reference": ref,
                    "status": "OK",
                    "profile": "default",
                    "status-message": "normal"}

        # Make tar.gz
        self.msg.append("Make tar.gz\n")
        self.answer({"message": ''.join(self.msg),
                     "percentage": 90})

        shutil.make_archive("%s/%s" % (VCS_TEMP_DIR, app_id),
                            "gztar", root_dir=VCS_TEMP_DIR,
                            base_dir=VCS_TEMP_DIR, logger=LOGGER)

        # Store archive
        self.msg.append("Store archive\n")
        self.answer({"message": ''.join(self.msg),
                     "percentage": 95})
        try:
            application_data = open("%s/%s.tar.gz" % (VCS_TEMP_DIR, app_id),
                                    'rb').read()
            yield Storage().write_app_data_future(app_id, application_data)
        except ServiceError as err:
            LOGGER.error(repr(err))
        except Exception as err:
            LOGGER.error(err)

        try:
            self.msg.append("Store information about application\n")
            self.answer({"message": ''.join(self.msg),
                         "percentage": 98})

            yield Storage().write_app_future(app_id, json.dumps(app_info))
            self.msg.append("Done\n")
            self.answer({"finished": True,
                         "id": app_id,
                         "percentage": 100,
                         "message": ''.join(self.msg)})
        except ServiceError as err:
            LOGGER.error(repr(err))
        except Exception as err:
            LOGGER.error(err)

    def _extract_commits(self):
        head = self.repo.head.get_object()
        for commit in self.repo.walk(head.oid, pygit2.GIT_SORT_TIME):
            yield  {'hash': commit.hex,
                    'message': commit.message,
                    'commit_date': commit.commit_time,
                    'author_name': commit.author.name,
                    'author_email': commit.author.email}
