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


__all__ = ['request', 'response', 'serving']


import logging

LOGGER = logging.getLogger('solo.web')

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    LOGGER.ERROR('You shall install Gevent, if wanna use gevent wsgi server')
    exit(1)
    
class GreenletServing(object):
    
    __slots__ = ('__local__', )

    def __init__(self):
        object.__setattr__(self, '__local__', {})

    def load(self, request, response):
        self.__local__[get_ident()] = {
            'request': request,
            'response': response
        }

    def __getattr__(self, name):
        try:
            return self.__local__[get_ident()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = get_ident()
        local = self.__local__
        try:
            local[ident][name] = value
        except KeyError:
            local[ident] = {name: value}

    def clear(self):
        """Clear all attributes of the current greenlet."""
        del self.__local__[get_ident()]


serving = GreenletServing()


class _ThreadLocalProxy(object):

    """From cherrypy  http://www.cherrypy.org/"""
    
    __slots__ = ['__attrname__', '__dict__']

    def __init__(self, attrname):
        self.__attrname__ = attrname

    def __getattr__(self, name):
        child = getattr(serving, self.__attrname__)
        return getattr(child, name)

    def __setattr__(self, name, value):
        if name in ("__attrname__", ):
            object.__setattr__(self, name, value)
        else:
            child = getattr(serving, self.__attrname__)
            setattr(child, name, value)

    def __delattr__(self, name):
        child = getattr(serving, self.__attrname__)
        delattr(child, name)

    def _get_dict(self):
        child = getattr(serving, self.__attrname__)
        d = child.__class__.__dict__.copy()
        d.update(child.__dict__)
        return d
    __dict__ = property(_get_dict)

    def __getitem__(self, key):
        child = getattr(serving, self.__attrname__)
        return child[key]

    def __setitem__(self, key, value):
        child = getattr(serving, self.__attrname__)
        child[key] = value

    def __delitem__(self, key):
        child = getattr(serving, self.__attrname__)
        del child[key]

    def __contains__(self, key):
        child = getattr(serving, self.__attrname__)
        return key in child

    def __len__(self):
        child = getattr(serving, self.__attrname__)
        return len(child)

    def __nonzero__(self):
        child = getattr(serving, self.__attrname__)
        return bool(child)
    # Python 3
    __bool__ = __nonzero__

# Create request and response object (the same objects will be used
#   throughout the entire life of the webserver, but will redirect
#   to the "serving" object)
request = _ThreadLocalProxy('request')
response = _ThreadLocalProxy('response')
