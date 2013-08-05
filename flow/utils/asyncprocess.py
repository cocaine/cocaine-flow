import subprocess
from multiprocessing import Process, Pipe

from cocaine.futures.chain import *
from cocaine.asio.ev import Loop

from tornado.ioloop import IOLoop


def asyncprocess(cmd, callback):
    ioloop = IOLoop.instance()
    PIPE = subprocess.PIPE
    pipe = subprocess.Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE,
                            stderr=PIPE, close_fds=True)
    fd = pipe.stderr.fileno()

    def recv(*args):
        data = pipe.stderr.readline()
        if data:
            callback(data)

        elif pipe.poll() is not None:
            ioloop.remove_handler(fd)
            callback(None)
    # read handler
    ioloop.add_handler(fd, recv, ioloop.READ)


class AsyncSubprocess(object):

    def __init__(self, cmd, ioloop=None):
        self.cmd = cmd
        self.ioloop = ioloop or IOLoop.instance()
        self.pipe = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     close_fds=True)

    def stdout_read(self):
        pass
