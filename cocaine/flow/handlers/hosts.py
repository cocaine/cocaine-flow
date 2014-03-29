from tornado import gen

from flow.handlers import AuthRequiredCocaineHandler


class Hosts(AuthRequiredCocaineHandler):
    @gen.coroutine
    def post(self, name):
        yield self.fw.host_add(name)
        self.ok()

    @gen.coroutine
    def put(self, name):
        yield self.post(name)

    @gen.coroutine
    def delete(self, name):
        yield self.fw.host_remove(name)
        self.ok()


class HostsList(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self):
        hosts = yield self.fw.host_list()
        self.send_json(hosts)
