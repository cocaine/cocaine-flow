# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="cocaine-flow",
    version="0.10.0-rc0",
    description="Cocaine Flow",
    long_description="Cocaine Management Tools",
    url="https://github.com/cocaine/cocaine-flow",
    author="Anton Tyurin",
    author_email="noxiouz@yandex.ru",
    license="BSD 2-Clause",
    platforms=["Linux", "BSD", "MacOS"],
    packages=["cocaine","cocaine.flow", 'cocaine.flow.storages', 'cocaine.flow.views', 'flask_pymongo'],
    package_data={'cocaine.flow': ['templates/*', 'static/style.css', 'static/bootstrap/css/*', 'static/bootstrap/js/*',
                                   'static/bootstrap/img/*', 'static/jquery.jeditable.js']},
    scripts=['cocaine/flow/cocaine-flow', 'cocaine/flow/cocaine-flow-setup'],
    data_files = [('/etc/ubic/service', ['scripts/cocaine-flow']),
                  ('/etc/cocaine-flow/',['exampleconf/settings.yaml']),
                  ('/var/log/cocaine-flow',[])],
    requires=["msgpack", "flask"]
)
