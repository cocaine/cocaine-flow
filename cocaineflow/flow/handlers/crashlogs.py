from tornado import gen

from flow.handlers import CocaineHanler


class CrashlogsList(CocaineHanler):
    @gen.coroutine
    def get(self, name):
        crashlogs = yield self.fw.crashlog_list(name)
        self.send_json(crashlogs)


class Crashlogs(CocaineHanler):
    @gen.coroutine
    def get(self, name, timestamp):
        crashlog = yield self.fw.crashlog_view(name, timestamp)
        self.write('\n'.join(crashlog))
