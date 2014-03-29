from tornado import gen

from cocaine.flow.handlers import AuthRequiredCocaineHandler


class Profiles(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self, name):
        result = yield self.fw.profile_read(name)
        self.send_json(result)

    @gen.coroutine
    def post(self, name):
        body = self.request.body
        yield self.fw.profile_upload(name, body)
        self.ok()

    @gen.coroutine
    def put(self, name):
        yield self.post(name)

    @gen.coroutine
    def delete(self, name):
        yield self.fw.profile_remove(name)
        self.ok()


class ProfilesList(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self):
        result = yield self.fw.profile_list()
        self.send_json(result)
