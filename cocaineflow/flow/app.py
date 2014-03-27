import tornado.web

from flow.handlers import profiles
from flow.handlers import hosts
from flow.handlers import runlists
from flow.handlers import groups

Application = tornado.web.Application([
    (r"/profiles/?", profiles.ProfilesList),
    (r"/profiles/(.+)", profiles.Profiles),

    (r"/hosts/(.+)", hosts.Hosts),
    (r"/hosts/?", hosts.HostsList),

    (r"/runlists/(.+)", runlists.Runlists),
    (r"/runlists/?", runlists.RunlistsList),

    (r"/groups/([^/]+)", groups.RoutingGroups),
    (r"/groups/([^/]+)/(.+)", groups.RoutingGroupsPushPop),
    (r"/groups/?", groups.RoutingGroupsList),
    (r"/groupsrefresh/([^/]*)", groups.RoutingGroupsRefresh),
], debug=True)
