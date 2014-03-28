import json

from tornado import web

from flow.flowcloud import FlowCloud


AuthHeaderName = "Authorization"


class CocaineHanler(web.RequestHandler):

    def prepare(self):
        self.fw = FlowCloud.guest()

    def send_json(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))

    def ok(self):
        self.send_json({})

    def write_error(self, *args, **kwargs):
        # hijack exception here
        super(CocaineHanler, self).write_error(*args, **kwargs)


class AuthRequiredCocaineHandler(CocaineHanler):
    def prepare(self):
        # check Authorization header
        try:
            token = self.request.headers[AuthHeaderName]
            self.fw = FlowCloud.authorized(token)
            return
        except KeyError:
            pass
        #
        # TBD: cookies
        #
        raise web.HTTPError(403)

    def get_current_user(self):
        return self.user
