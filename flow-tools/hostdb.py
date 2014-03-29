from cocaine.asio.engine import asynchronous
from cocaine.logging import Logger

namespace_prefix = "flow-users@"
HOSTS_TAG = ["flow-host"]

logger = Logger()

namespace_prefix = "flow-hosts@"


class HostDB(object):
    def __init__(self, storage, namespace):
        self.namespace = namespace_prefix + namespace
        self.storage = storage

    @asynchronous
    def hosts(self):
        yield self.storage.find(self.namespace, HOSTS_TAG)

    @asynchronous
    def add(self, hostname):
        yield self.storage.write(self.namespace, hostname,
                                 hostname, HOSTS_TAG)

    @asynchronous
    def remove(self, hostname):
        yield self.storage.remove(self.namespace,
                                  hostname)
