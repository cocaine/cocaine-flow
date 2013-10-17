#!/usr/bin/env python

from cocaine.worker import Worker
from app import *

W = Worker()

W.run({"get": get_applications_info,
	   "upload": upload_application,
	   "destroy": destroy})
