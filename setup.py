from setuptools import setup, find_packages
import sys
from solo import __version__

setup(
    name = 'solo',
    version = __version__,
    author = "Thomas Huang",
    author_email='lyanghwy@gmail.com',
    description = "Web Framework Based Gevent & Webob & Routes",
    license = "GPL",
    keywords = "Web Framework Based Gevent & Webob & Routes",
    url='https://github.com/thomashuang/solo',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires = ['setuptools', 'gevent', 'mako', 'routes'],
    test_suite='unittests',
    classifiers=(
        "Development Status :: Production/Alpha",
        "License :: GPL",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scheduler"
        )
    )