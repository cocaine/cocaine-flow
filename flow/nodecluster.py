from cocaine.services import Service
from cocaine.asio.engine import asynchronous
from cocaine.logging import Logger

from cocaine.tools.actions import app

log = Logger()


class NodeCluster(object):
    def __init__(self, hosts, logcallback):
        self.hosts = hosts
        self.logcallback = logcallback

    @asynchronous
    def start_app(self, appname, profilename):
        success = list()
        failed = list()
        hosts_count = len(self.hosts)
        for i, host in enumerate(self.hosts):
            item = "Start %s at host %d/%d %s" % (appname,
                                                  i + 1, hosts_count,
                                                  host)
            log.info(item)
            self.logcallback(item)
            nodeinstance = None
            try:
                nodeinstance = Service("node", blockingConnect=False)
                yield nodeinstance.connect(host=host)
                res = yield app.Start(nodeinstance,
                                      appname,
                                      profilename).execute()
                self.logcallback(str(res))
            except Exception as e:
                item = "Unable to connect to node at host %s %s" % (host, e)
                log.error(item)
                self.logcallback(item)
                failed.append(host)
            else:
                item = "App %s has been launched successfully" % appname
                log.info(item)
                self.logcallback(item)
                success.append(host)
            finally:
                if nodeinstance is not None:
                    nodeinstance.disconnect()
        yield (success, failed)

    @asynchronous
    def stop_app(self, appname):
        succeed = list()
        failed = list()
        hosts_count = len(self.hosts)
        for i, host in enumerate(self.hosts):
            log.info("Stop %s at host %d/%d %s" % (appname,
                                                   i, hosts_count,
                                                   host))
            nodeinstance = None
            try:
                nodeinstance = Service("node", blockingConnect=False)
                yield nodeinstance.connect(host=host)
                res = yield app.Stop(nodeinstance, appname).execute()
                self.logcallback(str(res))
            except Exception as e:
                item = "Unable to connect to node at host %s %s" % (host, e)
                log.error(item)
                self.logcallback(item)
                failed.append(host)
            else:
                item = "App %s has been stoped successfully" % appname
                log.info(item)
                self.logcallback(item)
                succeed.append(host)
            finally:
                if nodeinstance is not None:
                    nodeinstance.disconnect()
        yield (succeed, failed)
