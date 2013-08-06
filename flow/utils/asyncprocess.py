import subprocess

from cocaine.futures.chain import *

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
            try:
                callback(None)
            except StopIteration:
                pass
    # read handler
    ioloop.add_handler(fd, recv, ioloop.READ)
