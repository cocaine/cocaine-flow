import json

from cocaine.services import Service
from cocaine.logging import Logger
from cocaine.exceptions import ServiceError

FLOW_PROFILES = "cocaine_flow_profiles"
FLOW_PROFILES_TAG = "flow_profiles"

storage = Service("storage")
LOGGER = Logger()

def get(request, response):
    name = yield request.read()
    profile = None
    try:
        profile = yield storage.read(FLOW_PROFILES, name)
    except ServiceError as err:
        response.write({})
    else:
        response.write(json.loads(profile))
    response.close()
