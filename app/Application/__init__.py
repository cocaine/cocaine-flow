#!/usr/bin/env python

from cocaine.worker import Worker
from app import *

W = Worker()


def ping(request, response):
    yield request.read()
    response.write("OK")
    response.close()

W.run({"get": get_applications_info,
       "upload": upload_application,
       "update": update_application_info,
       "deploy": deploy_application,
       "destroy": destroy,
       "ping": ping})
