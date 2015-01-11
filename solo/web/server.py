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

import logging

LOGGER = logging.getLogger('solo.web')

class WebServer(object):

    """Adapter for a gevent.wsgi.WSGIServer."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.ready = False

    def start(self):
        """Start the GeventWSGIServer."""
        # We have to instantiate the server class here because its __init__
        from gevent.wsgi import WSGIServer

        self.ready = True
        LOGGER.debug('Starting Gevent WSGI Server...')
        self.httpd = WSGIServer(*self.args, **self.kwargs)
        self.httpd.serve_forever()

    def stop(self):
        """Stop the HTTP server."""
        LOGGER.debug('Stoping Gevent WSGI Server...')
        self.ready = False
        self.httpd.stop()