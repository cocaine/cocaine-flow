#!/usr/bin/env python
import logging
import socket
from flask import Flask
import sys
import yaml
from storages import init_storage
import views

try:
    from collections import Mapping as MappingType
except ImportError:
    import UserDict
    MappingType = (UserDict.UserDict, UserDict.DictMixin, dict)


def test_mapping(value):
    return isinstance(value, MappingType)


def create_app(settings_path='/etc/cocaine-flow/settings.yaml'):
    app = Flask(__name__)
    with open(settings_path) as f:
        app.config.update(**yaml.load(f))

    app.add_url_rule('/', view_func=views.home)
    app.add_url_rule('/register', view_func=views.register, methods=['GET', 'POST'])
    app.add_url_rule('/login', 'login', view_func=views.login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', view_func=views.logout)
    app.add_url_rule('/dashboard', 'dashboard', view_func=views.dashboard, methods=['GET', 'POST'])
    app.add_url_rule('/dashboard/edit', view_func=views.dashboard_edit, methods=['POST'])

    app.add_url_rule('/maintenance', endpoint='maintenance', view_func=views.maintenance, methods=['POST'])
    app.add_url_rule('/token', view_func=views.get_token, methods=['POST'])
    #Stats
    app.add_url_rule('/stats', 'stats', view_func=views.stats, methods=['GET'])
    app.add_url_rule('/stats/<string:alias>/<string:host>', endpoint='host_stats', view_func=views.host_stats, methods=['GET'])
    #Balances
    app.add_url_rule('/balances', 'balances', view_func=views.balances, methods=['GET'])
    app.add_url_rule('/balances/<string:group>/<string:app_name>', 'add_balances', view_func=views.add_balance_list, methods=['POST'])
    # Profiles
    app.add_url_rule('/profiles/<string:name>', endpoint='create_profile', view_func=views.create_profile, methods=['POST'])
    app.add_url_rule('/profiles/<string:name>', endpoint='create_profile', view_func=views.delete_profile, methods=['DELETE'])
    app.add_url_rule('/profiles', view_func=views.get_profiles, methods=['GET'])
    # Deploy and Undeploy
    app.add_url_rule('/exists/<string:prefix>/<string:postfix>', view_func=views.exists)
    app.add_url_rule('/upload', endpoint="upload", view_func=views.upload, methods=['GET', 'POST'])
    app.add_url_rule('/deploy/<string:runlist>/<string:uuid>/<string:profile>', endpoint="deploy",
                     view_func=views.deploy, methods=['POST'])
    app.add_url_rule('/undeploy/<string:runlist>/<string:uuid>/<string:profile>', endpoint="undeploy",
                     view_func=views.deploy, methods=['POST'])
    #Hosts
    app.add_url_rule('/hosts/', view_func=views.get_hosts, methods=['GET'])
    app.add_url_rule('/hosts/<string:alias>/<string:host>', endpoint="create_host", view_func=views.create_host, methods=['POST', 'PUT'])
    app.add_url_rule('/hosts/<string:alias>/<string:host>', endpoint='delete_host', view_func=views.delete_host, methods=['DELETE'])
    app.add_url_rule('/hosts/<string:alias>', endpoint='delete_alias', view_func=views.delete_alias, methods=['DELETE'])
    #Apps
    app.add_url_rule('/apps/', view_func=views.get_apps, methods=['GET'])
    app.add_url_rule('/app/<string:app_name>', view_func=views.delete_app, methods=['DELETE'])
    app.add_url_rule('/app/start/<string:uuid>/<string:profile>', view_func=views.start_app, methods=['POST'])
    app.add_url_rule('/app/stop/<string:uuid>', view_func=views.stop_app, methods=['POST'])
    #Runlists
    app.add_url_rule('/runlists', view_func=views.get_runlists)
    app.add_url_rule('/runlists/<string:name>', endpoint='create_runlist', view_func=views.create_runlist, methods=['POST'])
    app.add_url_rule('/runlists/<string:name>', endpoint='delete_runlist', view_func=views.delete_runlist, methods=['DELETE'])
    app.add_url_rule('/runlists_apps/', view_func=views.get_runlists_apps, methods=['GET'])

    # JSON API
    app.add_url_rule('/api/auth', view_func=views.auth, methods=['POST'])
    app.add_url_rule('/api/register', view_func=views.register_json, methods=['POST'])
    app.add_url_rule('/api/userinfo', view_func=views.userinfo, methods=['GET'])
    app.add_url_rule('/api/logout', view_func=views.logout_json, methods=['GET'])

    app.error_handler_spec[None][500] = views.error_handler

    init_storage(app)

    logging.basicConfig(level=logging.DEBUG)

    if 'mapping' not in app.jinja_env.tests:
        app.jinja_env.tests['mapping'] = test_mapping

    return app


if __name__ == '__main__':
    if len(sys.argv) == 2:
        app = create_app(sys.argv[1])
    else:
        app = create_app()

    app.run(debug=True, host=app.config.get('HOSTNAME', socket.gethostname()), port=int(app.config['PORT']))
