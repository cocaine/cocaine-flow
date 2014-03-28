from tornado import gen

from flow.handlers import CocaineHanler


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
        yield self.fw.signin(name, password)
        token = self.token.pack_user({"name": name,
                                      "password": password, })
        self.write(token)
