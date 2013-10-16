import json

from cocaine.services import Service
from cocaine.logging import Logger
from cocaine.exceptions import ServiceError

FLOW_APPS_DATA = "cocaine_flow_apps_data"
FLOW_APPS_DATA_TAG = "flow_apps_data"

FLOW_APPS = "cocaine_flow_apps"
FLOW_APPS_TAG = "apps"

storage = Service("storage")
LOGGER = Logger()


def get(request, response):
    yield request.read()
    items = yield storage.find(FLOW_APPS, [FLOW_APPS_TAG])
    res = []
    for item in items:
        tmp = yield storage.read(FLOW_APPS, item)
        try:
            res.append(json.loads(tmp))
        except ServiceError as err:
            LOGGER.error(str(err))
    response.write(res)
    response.close()
    

