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

import tornado.platform.twisted

from twisted.cred.portal import Portal
from twisted.conch import checkers
from twisted.conch.ssh.keys import Key


def start_ssh(sockets, privatekeyfile, io_loop=None):
    reactor = tornado.platform.twisted.install(io_loop)

    # Import here to prevent initialization of default reactor
    from twisted.conch.ssh.factory import SSHFactory
    from twisted.conch.unix import UnixSSHRealm

    class SSHServer(SSHFactory):
        portal = Portal(UnixSSHRealm())
        portal.registerChecker(checkers.UNIXPasswordDatabase())
        portal.registerChecker(checkers.SSHPublicKeyDatabase())

        def __init__(self, privkey):
            pubkey = '.'.join((privkey, 'pub'))
            self.privateKeys = {'ssh-rsa': Key.fromFile(privkey)}
            self.publicKeys = {'ssh-rsa': Key.fromFile(pubkey)}

    for sock in sockets:
        reactor.adoptStreamPort(sock.fileno(), sock.family, SSHServer(privatekeyfile))
