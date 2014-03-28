from tornado import gen

from flow.handlers import AuthRequiredCocaineHandler


class Buildlogs(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self, name):
        buildlog = yield self.fw.buildlog_read(name)
        self.write(buildlog)


class BuildlogsList(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self):
        buildlogs = yield self.fw.buildlog_list(self.user)
        self.send_json(buildlogs)
