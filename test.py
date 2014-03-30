import json
import urllib
import time

from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop

from cocaine.flow.app import FlowRestServer

test_runlist_name = "sometestrunlist"
test_runlists = "{}"

test_profile_name = "sometestprofile"
test_profile = "{}"

test_auth = {
    "name": "noxiouztest9",
    "password": "qwerty",
}


class FlowTestCase(AsyncHTTPTestCase):
    def get_new_ioloop(self):
        return IOLoop.instance()

    def get_app(self):
        settings = {
            "debug": True,
            "token_key": b"aaaaaaaaaaaaaaaa",
            "cocaine_port": 10053,
            "cocaine_host": "localhost",
            "docker": "http://192.168.57.100:3138",
            "registry": "192.168.57.100:5000",
        }
        return FlowRestServer(**settings)


def create_fake_user(func):
    def wrapper(self):
        self.reg()
        try:
            func(self)
        finally:
            self.unreg()
    return wrapper


class FlowTest(FlowTestCase):

    def reg(self):
        self.user = "auth_testuser"
        self.password = "auth_password"
        self.auth = {"name": self.user,
                     "password": self.password,
                     }

        r = self.fetch('/flow/v1/signup',
                       method="POST",
                       body=urllib.urlencode(self.auth))

        r = self.fetch('/flow/v1/gentoken',
                       method="POST",
                       body=urllib.urlencode(self.auth))
        self.assertEqual(200, r.code)
        self.token = r.body

    def unreg(self):
        r = self.fetch('/flow/v1/removeuser/' + self.user,
                       method="DELETE",
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)
        self.token = ""

    @create_fake_user
    def test_runlists(self):
        response = self.fetch('/flow/v1/runlists/',
                              headers={"Authorization": self.token})
        self.assertEqual(200, response.code)

        runlists = json.loads(response.body)
        for item in runlists:
            response = self.fetch('/flow/v1/runlists/%s' % item,
                                  headers={"Authorization": self.token})
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

    @create_fake_user
    def test_apps(self):
        # add test host
        r = self.fetch('/flow/v1/hosts/localhost',
                       method="PUT",
                       body="",
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)

        # upload application
        version = int(time.time())
        with open("testapp/testapp.tar.gz", 'rb') as f:
            r = self.fetch('/flow/v1/apps/bullet/%d' % version,
                           headers={"Authorization": self.token},
                           body=f.read(),
                           method="POST")
            self.assertEqual(200, r.code)

        # application list
        r = self.fetch('/flow/v1/apps',
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)
        apps = json.loads(r.body)

        # deploy application
        args = "profile=TEST&runlist=TEST&weight=100"
        r = self.fetch('/flow/v1/deployapp/bullet/%d?%s' % (version, args),
                       method="POST",
                       body="",
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)

        # start application
        r = self.fetch('/flow/v1/startapp/bullet/%d?profile=TEST' % version,
                       method="POST",
                       body="",
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)

        for app in apps:
            # get application info
            r = self.fetch('/flow/v1/apps/%(name)s/%(version)s' % app,
                           headers={"Authorization": self.token})
            self.assertEqual(200, r.code)
            # Add body assertion

        # stop application
        r = self.fetch('/flow/v1/stopapp/bullet/%d?profile=TEST' % version,
                       method="POST",
                       body="",
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)

        # delete test host
        r = self.fetch('/flow/v1/hosts/localhost',
                       method="DELETE",
                       headers={"Authorization": self.token})

    @create_fake_user
    def test_profile(self):
        response = self.fetch('/flow/v1/profiles/',
                              headers={"Authorization": self.token})
        self.assertEqual(200, response.code)

        profiles = json.loads(response.body)
        for item in profiles:
            response = self.fetch('/flow/v1/profiles/%s' % item,
                                  headers={"Authorization": self.token})
            self.assertEqual(200, response.code)

        r = self.fetch('/flow/v1/profiles/%s' % test_profile_name,
                       headers={"Authorization": self.token},
                       body=test_profile,
                       method="POST")
        self.assertEqual(200, r.code, "Profile upload failed")
        self.assertEqual({}, json.loads(r.body))

        r = self.fetch('/flow/v1/profiles/%s' % test_profile_name,
                       headers={"Authorization": self.token},
                       method="DELETE")
        self.assertEqual(200, r.code, "Profile delete failed")
        self.assertEqual({}, json.loads(r.body))

    @create_fake_user
    def test_host(self):
        r = self.fetch('/flow/v1/hosts/' + "testHost",
                       method="PUT",
                       body="",
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)

        r = self.fetch('/flow/v1/hosts',
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)
        self.assertIn('testHost', json.loads(r.body))

        r = self.fetch('/flow/v1/hosts/' + "testHost",
                       method="DELETE",
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)

        r = self.fetch('/flow/v1/hosts',
                       headers={"Authorization": self.token})
        self.assertEqual(200, r.code)
        self.assertTrue(not 'testHost'in json.loads(r.body))


class FlowTestAuth(FlowTestCase):

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
        token = r.body

        r = self.fetch('/flow/v1/removeuser/' + test_auth['name'],
                       method="DELETE",
                       headers={"Authorization": token})
        self.assertEqual(200, r.code)
