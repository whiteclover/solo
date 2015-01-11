#!/usr/bin/env python

from solo.web.server import WebServer
from solo.web.app import App

class HelloRoot(object):

    def index(self):
        return "Hello World!"

    def page(self, page):
        return page

class HelloApp(App):

    def initialize(self):
        ctl = HelloRoot()
        route = self.route()
        route.mapper.explicit = False
        route.connect('index', '/', controller=ctl, action='index')
        route.connect('page', '/page/:page', controller=ctl, action='page')


if __name__ == '__main__':
    app = HelloApp()
    WebServer(('127.0.0.1', 8080), app, log=None).start()
