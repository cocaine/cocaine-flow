import subprocess

import tornado.ioloop


def asyncprocess(obj, cmd, callback):
    ioloop = tornado.ioloop.IOLoop.instance()
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
