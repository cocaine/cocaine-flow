from tornado import gen

from cocaine.flow.handlers import AuthRequiredCocaineHandler


class Runlists(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self, name):
        rl = yield self.fw.runlist_read(name)
        self.send_json(rl)

    # @gen.coroutine
    # def post(self, name):
    #     yield self.fw.runlist_add(name)
    #     self.ok()

    # @gen.coroutine
    # def put(self, name):
    #     yield self.post(name)

    @gen.coroutine
    def delete(self, name):
        yield self.fw.runlist_remove(name)
        self.ok()


class RunlistsList(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self):
        runlists = yield self.fw.runlist_list()
        self.send_json(runlists)
