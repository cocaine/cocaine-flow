#!/usr/bin/env python
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

from setuptools import setup


setup(
    name="cocaine-flow",
    version="0.11.7.0",
    author="Anton Tyurin",
    author_email="noxiouz@yandex.ru",
    maintainer='Anton Tyurin',
    maintainer_email='noxiouz@yandex.ru',
    url="https://github.com/cocaine/cocaine-flow",
    description="Cocaine Flow for Cocaine Application Cloud.",
    long_description="REST server for Cocaine cloud",
    license="LGPLv3+",
    platforms=["Linux", "BSD", "MacOS"],
    namespace_packages=['cocaine'],
    include_package_data=True,
    zip_safe=False,
    packages=[
        "cocaine",
        "cocaine.flow",
        "cocaine.flow.handlers",
    ],
    install_requires=[
        "cocaine >= 0.11.1.0",
        "tornado >= 3.1",
        "cocaine-tools >= 0.11.4.0",
        "msgpack_python",
    ],
    scripts=[
        "cocaine-flow"
    ],
    classifiers=[
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
    ],
)
