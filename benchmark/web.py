#!/usr/bin/env python

from solo.web.app import App

class HelloRoot(object):

    def index(self):
        return "Hello World!"

class HelloApp(App):

    def initialize(self):
        ctl = HelloRoot()
        route = self.route()
        route.mapper.explicit = False
        route.connect('index', '/', controller=ctl, action='index')

app = HelloApp()

if __name__ == '__main__':
    from gevent.wsgi import WSGIServer
    http_server = WSGIServer(('', 8080), app, log=None)
    http_server.serve_forever()