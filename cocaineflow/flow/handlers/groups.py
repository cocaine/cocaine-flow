from tornado import gen

from flow.handlers import AuthRequiredCocaineHandler


class RoutingGroups(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self, name):
        result = yield self.fw.group_read(name)
        self.send_json(result)

    @gen.coroutine
    def post(self, name):
        yield self.fw.group_create(name)
        self.ok()

    @gen.coroutine
    def put(self, name):
        yield self.post(name)

    @gen.coroutine
    def delete(self, name):
        yield self.fw.group_remove(name)
        self.ok()


class RoutingGroupsList(AuthRequiredCocaineHandler):
    @gen.coroutine
    def get(self):
        result = yield self.fw.group_list()
        self.send_json(result)


class RoutingGroupsPushPop(AuthRequiredCocaineHandler):
    @gen.coroutine
    def put(self, group, app):
        weight = self.get_argument("weight")
        yield self.fw.group_pushapp(group, app, weight)
        self.ok()

    @gen.coroutine
    def delete(self, group, app):
        yield self.fw.group_popapp(group, app)
        self.ok()


class RoutingGroupsRefresh(AuthRequiredCocaineHandler):
    @gen.coroutine
    def post(self, name):
        yield self.fw.group_refresh(name)
        self.ok()
