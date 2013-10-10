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

from setuptools import setup

setup(
    name="cocaine_flow",
    version="0.10.1",
    description="Cocaine Flow",
    long_description="Web interface for cloud",
    url="https://github.com/cocaine/cocaine-flow",
    author="Anton Tyurin",
    author_email="noxiouz@yandex.ru",
    license="LGPLv3+",
    platforms=["Linux", "BSD", "MacOS"],
    packages=[
        "flow",
        "flow.views",
        "flow.utils"
    ],
    data_files = [
        ('/usr/lib/flow/Application', ['app/Application/app.py', 'app/Application/manifest.json', 'app/Application/__init__.py']),
        ('/usr/lib/flow/Profile', ['app/Profile/profile.py', 'app/Profile/manifest.json', 'app/Profile/__init__.py']),
    ],
    install_requires=["msgpack_python", "tornado", "pygit2", "tornadio2"],
    scripts=["cocaine-flow"]
)
