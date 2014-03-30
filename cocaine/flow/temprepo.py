# encoding: utf-8
#
#    Copyright (c) 2013-2014+ Anton Tyurin <noxiouz@yandex.ru>
#    Copyright (c) 2013-2014 Other contributors as noted in the AUTHORS file.
#
#    This file is part of Cocaine.
#
#    Cocaine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
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
import shutil
import tarfile
import tempfile

try:
    from io import BytesIO  # py3
except ImportError:
    from cStringIO import StringIO as BytesIO  # py2

logger = logging.getLogger()


class TempDir(object):
    def __init__(self):
        self.logger = logging.getLogger()
        self.path = tempfile.mkdtemp()
        self.logger.debug("Initialize tempdir %s", self.path)

    def clean(self):
        self.logger.debug("Remove tempdir %s", self.path)
        shutil.rmtree(self.path, ignore_errors=True)


def unpack_archive(data):
    fileobj = BytesIO(data)
    try:
        with tarfile.open(fileobj=fileobj) as archive:
            # NOTE: this dir could be read only by the same UID
            tempdir = TempDir()
            archive.extractall(tempdir.path)
    except Exception as err:
        logger.error(err)
    else:
        return tempdir


