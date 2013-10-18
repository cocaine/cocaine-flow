"""Control cluster"""
from tornado import web
from flow.utils.requesthandler import CocaineRequestHandler
from flow.utils.route import Route



from cocaine.futures.chain import source
from cocaine.services import Service
from cocaine.exceptions import ChokeEvent

FLOW_HOSTS = "cocaine_flow_hosts"
FLOW_HOSTS_TAG = "cocaine_flow_hosts_tag"


@Route(r"/flow/hosts")
class Hosts(CocaineRequestHandler):

    def get(self):
        hosts = Service('storage').find(FLOW_HOSTS, [FLOW_HOSTS_TAG]).get()
        self.finish('\n'.join(hosts))

    def put(self):
        raw_hosts = self.get_argument("hosts")
        hosts = raw_hosts.split(',')
        storage = Service('storage')
        for host in hosts:
            try:
                storage.write(FLOW_HOSTS, host, host, [FLOW_HOSTS_TAG]).get()
            except ChokeEvent:
                pass
        self.finish("ok")

    def delete(self):
        raw_hosts = self.get_argument("hosts")
        hosts = raw_hosts.split(',')
        storage = Service('storage')
        for host in hosts:
            try:
                storage.remove(FLOW_HOSTS, host).get()
            except ChokeEvent:
                pass
        self.finish("ok")
