from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop

from flow.app import Application


class FlowTestCase(AsyncHTTPTestCase):
    def get_new_ioloop(self):
        return IOLoop.instance()


class FlowTest(FlowTestCase):
    def get_app(self):
        return Application

    def test_runlists(self):
        response = self.fetch('/flow/v1/runlists/')
        self.assertEqual(200, response.code)
