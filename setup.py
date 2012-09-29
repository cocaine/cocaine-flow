# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="cocaine-flow",
    version="0.10.0",
    description="Cocaine Flow",
    long_description="Cocaine Management Tools",
    url="https://github.com/cocaine/cocaine-flow",
    author="Alexander Eliseev",
    author_email="alex@inkvi.com",
    license="BSD 2-Clause",
    platforms=["Linux", "BSD", "MacOS"],
    packages=["cocaine.flow", 'cocaine.flow.storages'],
    package_data={'cocaine.flow': ['templates/*', 'static/style.css', 'static/bootstrap/css/*', 'static/bootstrap/js/*',
                                   'static/bootstrap/img/*']},
    requires=["msgpack"]
)
