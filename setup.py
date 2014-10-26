#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013+ Anton Tyurin <noxiouz@yandex.ru>
# Copyright (c) 2013-2014 Other contributors as noted in the AUTHORS file.
#
# This file is part of Cocaine flow
#
# Cocaine is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Cocaine is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import setuptools


__author__ = 'Anton Tiurin'
__copyright__ = 'Copyright 2013+'
__credits__ = []

__license__ = 'LGPLv3+'
__version__ = '0.0.1'
__maintainer__ = 'Anton Tiurin'
__email__ = 'noxiouz@yandex.ru'
__status__ = 'Production'

__title__ = 'cocaine-flow'

__url__ = 'https://github.com/cocaine/cocaine-flow'
__description__ = 'Cocaine flow'
d = 'https://github.com/cocaine/cocaine-flow/archive/master.zip'

setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__maintainer__,
    maintainer_email=__email__,
    url=__url__,
    description=__description__,
    long_description=open('./README.md').read(),
    download_url=d,
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Programming Language :: Python :: Implementation :: PyPy',
                 'Operating System :: OS Independent',
                 'Topic :: Utilities',
                 'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)'],
    platforms=['Independent'],
    zip_safe=False,
    license=open('./LICENSE').read(),
    namespace_packages=['cocaine'],
    packages=['cocaine'],
    install_requires=open('./requirements.txt').read(),
    tests_require=open('./tests/requirements.txt').read(),
    test_suite='nose.collector'
)
