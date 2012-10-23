# -*- coding: utf-8 -*-
from __future__ import absolute_import
from flask import current_app
from .storage import Storage
from elliptics import Logger, Node
import traceback


class Elliptics(Storage):
    def __init__(self, nodes, groups):
        self.node = Node(Logger("/tmp/cocainoom-elliptics.log"))
        for host, port in nodes.iteritems():
            try:
                self.node.add_remote(host, port)
            except RuntimeError:
                # already connected to the host
                traceback.print_exc()

        try:
            from elliptics import Session
            self.storage = Session(self.node)
        except ImportError:
            self.storage = self.node

        self.storage.add_groups(groups)

    def key(self, key, *args):
        prefix = key
        postfix = args[0]

        if type(postfix) in set([tuple, list, set]):
            return type(postfix)(["%s\0%s" % (prefix, p) for p in postfix])

        return "%s\0%s" % (prefix, postfix)
