#!/usr/bin/env python
# Copyright (C) 2015 Thomas Huang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.




from webob import exc
from webob import Request, Response

import logging
from sys import exc_info

from solo.web.ctx import serving
from solo.web.hook import HookMap
from solo.web.dispatcher import RoutesDispatcher

LOGGER = logging.getLogger('solo.web')



class App(object):


    hookpoints = ['on_start_resource', 'before_handler',
                'on_end_resource', 'on_end_request',
                'before_error_response', 'after_error_response']


    def __init__(self, name='Lilac', encoding='utf8', debug=False, dispatcher=None):
        self.dispatcher = dispatcher or RoutesDispatcher()
        self.name = name
        self.error_pages = {}
        self.encoding = encoding
        self.debug = debug
        self.hooks = HookMap()
        self.error_response = self._error_response
        self.initialize()

    def initialize(self):
        pass

    def route(self):
        return self.dispatcher

    def attach(self, point, callback, failsafe=None, priority=None, **kwargs):
        if point not in self.hookpoints:
            return
        self.hooks.attach(point, callback, failsafe, priority, **kwargs)

    def asset(self, name, path, asset_path, default_filename=None, block_size=None):
        """Set servering Static directory"""
        from solo.web.asset import AssetController
        path = '' if path == '/' else path
        ctl = AssetController(asset_path, default_filename, block_size)
        self.dispatcher.connect(name, path + "/{path:.*?}", controller=ctl, action='asset', conditions=dict(method=["HEAD", "GET"]))


    def error_page(self, code, callback):
        if type(code) is not int:
            raise TypeError("code:%d is not int type" %(code))
        self.error_pages[str(code)] = callback

    def __call__(self, environ, start_response):
        try:
            try:
                request = Request(environ)
                response = Response()
                serving.load(request, response)
                if request.charset is None:
                    request.charset = self.encoding

                self.hooks.run('on_start_resource')

                path_info = environ['PATH_INFO']
                action, handler = self.dispatcher.match(request, path_info)
                body = None
                self.hooks.run('before_handler')

                if handler:
                    body = handler()
                    if type(body) is str:
                        response.body = body
                    elif body:
                        response.text = body
                    self.hooks.run('on_end_resource')
                    return response(environ, start_response)
                else:
                    raise exc.HTTPNotFound('Path %s Not Found' % (path_info)) 

            except exc.HTTPRedirection as e:
                serving.response.location = e.location
                serving.response.status = e.status
                response = serving.response
                self.hooks.run('on_end_resource')
            except exc.HTTPException as e:
                response = serving.response = self.handle_error_page(request, response, e)
            except Exception as e:
                LOGGER.error(e)
                self.error_response(request, response, e)
            return response(environ, start_response)
        finally:
            try:
                self.hooks.run('on_end_request')
            finally:
                serving.clear()


    def handle_error_page(self, request, response, exception):
        """Handle the last unanticipated exception. (Core)"""
        try:
            self.hooks.run("before_error_response")
            response.status = exception.status
            #response.status = exception.status
            handler = self.error_pages.get(str(exception.code), None)
            if handler:
                body = handler()
                if type(body) is str:
                    response.body = body
                elif text:
                    response.text = body
                return response
            else:
                return exception
        finally:
            self.hooks.run("after_error_response")

    def _error_response(self, request, response, exception):
        """Handle the unknow exception and also throw 5xx status and message to frontend"""
        cls, e, tb = exc_info()

        LOGGER.exception('Unhandled Error: %s', e)

        response.status_code = 500
        response.content_type = 'text/html; charset=UTF-8'

        if request.method != 'HEAD':
            response.unicode_body = u"""<html>
<head><title>Internal Server Error </title></head>
<body><p>An error occurred: <b>%s</b></p></body>
</html> 
""" % (str(e))

