# -*- coding: utf-8 -*-
from storages.storage import Storage
from elliptics_wrapper import Logger, Node
import api_settings as settings
import traceback


class Elliptics(Storage):
    def __init__(self):
        self.storage = Node(Logger("/tmp/cocainoom-elliptics.log"))
        for host, port in settings.ELLIPTICS_NODES.iteritems():
            try:
                self.storage.add_remote(host, port)
            except RuntimeError:
                # already connected to the host
                traceback.print_exc()
        self.storage.add_groups(settings.ELLIPTICS_GROUPS)

    def key(self, key, *args):
        prefix = key
        postfix = args[0]

        if type(postfix) in set([tuple, list, set]):
            return type(postfix)(["%s\0%s" % (prefix, p) for p in postfix])

        return "%s\0%s" % (prefix, postfix)
