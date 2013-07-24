#
#   Copyright (c) 2011-2013 Anton Tyurin <noxiouz@yandex.ru>
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

from tornado.options import define
from tornado.options import parse_config_file
from tornado.options import parse_command_line

define("SECRET_KEY")
define("port", default=8001, type=int, help="listening port number")
define("daemon", default=False, type=bool, help="daemonize")
define("pidfile", default="/var/run/tornado", type=str, help="pidfile")
#define("user", default=DEFAULT_USER, type=str, help="Set process's username")
parse_config_file("./config")
actions = parse_command_line()
