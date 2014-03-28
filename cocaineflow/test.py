import json
import urllib

from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop

from flow.app import Application

test_runlist_name = "sometestrunlist"
test_runlists = "{}"

test_profile_name = "sometestprofile"
test_profile = "{}"

test_auth = {
    "name": "noxiouztest4",
    "password": "qwerty",
}


class FlowTestCase(AsyncHTTPTestCase):
    def get_new_ioloop(self):
        return IOLoop.instance()


class FlowTest(FlowTestCase):
    def get_app(self):
        return Application

    def test_runlists(self):
        response = self.fetch('/flow/v1/runlists/')
        self.assertEqual(200, response.code)

        runlists = json.loads(response.body)
        for item in runlists:
            response = self.fetch('/flow/v1/runlists/%s' % item)
            self.assertEqual(200, response.code)

        # r = self.fetch('/flow/v1/runlists/%s' % test_runlist_name,
        #                body=test_runlists,
        #                method="POST")
        # self.assertEqual(200, r.code, "Runlist upload failed")
        # self.assertEqual({}, json.loads(r.body))

        # r = self.fetch('/flow/v1/runlists/%s' % test_runlist_name,
        #                method="DELETE")
        # self.assertEqual(200, r.code, "Runlist delete failed")
        # self.assertEqual({}, json.loads(r.body))

    def test_profile(self):
        response = self.fetch('/flow/v1/profiles/')
        self.assertEqual(200, response.code)

        profiles = json.loads(response.body)
        for item in profiles:
            response = self.fetch('/flow/v1/profiles/%s' % item)
            self.assertEqual(200, response.code)

        r = self.fetch('/flow/v1/profiles/%s' % test_profile_name,
                       body=test_profile,
                       method="POST")
        self.assertEqual(200, r.code, "Profile upload failed")
        self.assertEqual({}, json.loads(r.body))

        r = self.fetch('/flow/v1/profiles/%s' % test_profile_name,
                       method="DELETE")
        self.assertEqual(200, r.code, "Profile delete failed")
        self.assertEqual({}, json.loads(r.body))

    def test_auth(self):
        r = self.fetch('/flow/v1/signup',
                       method="POST",
                       body=urllib.urlencode(test_auth))
        self.assertEqual(200, r.code)

        r = self.fetch('/flow/v1/signin',
                       method="POST",
                       body=urllib.urlencode(test_auth))
        self.assertEqual(200, r.code)

        r = self.fetch('/flow/v1/gentoken',
                       method="POST",
                       body=urllib.urlencode(test_auth))
        self.assertEqual(200, r.code)
