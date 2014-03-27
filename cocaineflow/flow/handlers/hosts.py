from tornado import gen

from flow.handlers import CocaineHanler


class Hosts(CocaineHanler):
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


class HostsList(CocaineHanler):
    @gen.coroutine
    def get(self):
        hosts = yield self.fw.host_list()
        self.send_json(hosts)
