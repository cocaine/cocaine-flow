import tornado.web

from flow.handlers import auth
from flow.handlers import crashlogs
from flow.handlers import groups
from flow.handlers import hosts
from flow.handlers import profiles
from flow.handlers import runlists

Application = tornado.web.Application([
    (r"/flow/v1/profiles/?", profiles.ProfilesList),
    (r"/flow/v1/profiles/(.+)", profiles.Profiles),

    (r"/flow/v1/hosts/(.+)", hosts.Hosts),
    (r"/flow/v1/hosts/?", hosts.HostsList),

    (r"/flow/v1/runlists/(.+)", runlists.Runlists),
    (r"/flow/v1/runlists/?", runlists.RunlistsList),

    (r"/flow/v1/groups/([^/]+)", groups.RoutingGroups),
    (r"/flow/v1/groups/([^/]+)/(.+)", groups.RoutingGroupsPushPop),
    (r"/flow/v1/groups/?", groups.RoutingGroupsList),
    (r"/flow/v1/groupsrefresh/([^/]*)", groups.RoutingGroupsRefresh),

    (r"/flow/v1/crashlogs/([^/]+)", crashlogs.CrashlogsList),
    (r"/flow/v1/crashlogs/([^/]+)/([^/]+)", crashlogs.Crashlogs),

    (r"/flow/v1/signup", auth.SignUp),
    (r"/flow/v1/signin", auth.SignIn),
    (r"/flow/v1/gentoken", auth.GenToken),
], debug=True)
