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
import pygit2


def main(path):
    repo = pygit2.repository.Repository(path)
    head = repo.head.get_object()
    for i in repo.walk(head.oid, pygit2.GIT_SORT_TIME):
        d = dict()
        d["message"] = i.message
        d["hash"] = i.hex
        d["author"] = "%s <%s>" % (i.author.name, i.author.email)
        d["time"] = i.commit_time
        yield d


if __name__ == "__main__":
    for i in main("/Users/noxiouz/Documents/github/cocaine-flow"):
        print i
