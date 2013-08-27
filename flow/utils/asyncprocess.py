import subprocess

from cocaine.futures.chain import Deferred

from tornado.ioloop import IOLoop


def guard(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception:
            pass
    return wrapper


def asyncprocess(cmd, callback, cwd=None):
    callback = guard(callback)
    ioloop = IOLoop.instance()
    pipe = subprocess.Popen(cmd, shell=True,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            close_fds=True,
                            cwd=cwd)
    future = Deferred()
    fd_err = pipe.stderr.fileno()
    #fd_out = pipe.stdout.fileno()

    def recv(*args):
        if pipe.poll() is not None:
            callback(pipe.stderr.readline())
            ioloop.remove_handler(fd_err)
            future.ready(pipe.poll())
        else:
            callback(pipe.stderr.readline())
    # read handler
    ioloop.add_handler(fd_err, recv, ioloop.READ)
    return future

