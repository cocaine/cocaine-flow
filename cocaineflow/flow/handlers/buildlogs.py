from tornado import gen

from flow.handlers import CocaineHanler


class Buildlogs(CocaineHanler):
    @gen.coroutine
    def get(self):
        pass
