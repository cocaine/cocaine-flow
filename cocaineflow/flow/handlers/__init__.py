import json

from tornado import web

from flow.flowcloud import FlowCloud
from flow.token import Token


class CocaineHanler(web.RequestHandler):
    fw = FlowCloud.instance()
    token = Token()

    def send_json(self, data):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps(data))

    def ok(self):
        self.send_json({})

    def write_error(self, *args, **kwargs):
        # hijack exception here
        super(CocaineHanler, self).write_error(*args, **kwargs)

    def get_current_user(self):
        pass