from tornado import gen

from cocaine.flow.handlers import CocaineHanler
from cocaine.flow.handlers import AuthRequiredCocaineHandler


class SignUp(CocaineHanler):
    @gen.coroutine
    def post(self):
        name = self.get_argument("name")
        password = self.get_argument("password")
        yield self.fw.signup(name, password)
        self.ok()


class SignIn(CocaineHanler):
    @gen.coroutine
    def post(self):
        name = self.get_argument("name")
        password = self.get_argument("password")
        yield self.fw.signin(name, password)
        self.ok()


class GenToken(CocaineHanler):
    @gen.coroutine
    def post(self):
        name = self.get_argument("name")
        password = self.get_argument("password")
        # TBD: Merge it into private method
        yield self.fw.signin(name, password)
        token = self.fw.gentoken(name, password)
        self.write(token)


class RemoveUser(AuthRequiredCocaineHandler):
    @gen.coroutine
    def delete(self, name):
        yield self.fw.user_remove(name)
        self.ok()
