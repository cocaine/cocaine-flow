#!/usr/bin/env python
from flask import Flask
from flask.ext.pymongo import PyMongo
import views
import api_settings as settings

def init_elliptics():
    from elliptics import Logger, Node
    node = Node(Logger("/tmp/cocainoom-elliptics.log"))
    for host, port in settings.ELLIPTICS_NODES.iteritems():
        node.add_remote(host, port)
    node.add_groups(settings.ELLIPTICS_GROUPS)
    return node


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('api_settings.py')

    app.add_url_rule('/', view_func=views.home)
    app.add_url_rule('/register', view_func=views.register, methods=['GET', 'POST'])
    app.add_url_rule('/login', 'login', view_func=views.login, methods=['GET', 'POST'])
    app.add_url_rule('/logout', view_func=views.logout)
    app.add_url_rule('/dashboard', 'dashboard', view_func=views.dashboard, methods=['GET', 'POST'])
    app.add_url_rule('/profile/<string:name>', view_func=views.create_profile, methods=['POST'])
    app.add_url_rule('/read', view_func=views.read)
    app.add_url_rule('/upload', endpoint="uploadrepo", view_func=views.upload_repo, methods=['POST'])
    app.add_url_rule('/upload/<string:ref>', endpoint="upload", view_func=views.upload, methods=['POST'])

    app.mongo = PyMongo(app)
    app.elliptics = init_elliptics()

    return app


def install(username, password):
    app = create_app()
    with app.test_request_context():
        return views.create_user(username, password, admin=True)


if __name__ == '__main__':
    import api_settings as settings
    app = create_app()
    app.run(debug=True, host=settings.HOSTNAME)
