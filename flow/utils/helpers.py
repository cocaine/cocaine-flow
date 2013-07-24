import json
import logging

from flow.utils.storage import Storage

logger = logging.getLogger()


def get_applications(answer):
    try:
        items = yield Storage().list_app_future()
    except Exception:
        logger.exception()
    res = []
    for item in items:
        tmp = yield Storage().read_app_future(item)
        try:
            res.append(json.loads(tmp))
        except Exception:
            logger.exception()
    answer({"apps": res})
