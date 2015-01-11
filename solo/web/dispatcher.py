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
from solo.web.ctx import serving
import routes
from sys import exc_info

try:
    import inspect
except ImportError:
    test_callable_spec = lambda callable, args, kwargs: None

import types
try:
    classtype = (type, types.ClassType)
except AttributeError:
    classtype = type
    
import logging

LOGGER = logging.getLogger('solo.web')


class RoutesDispatcher(object):

    """A Routes based dispatcher for CherryPy."""

    def __init__(self, **mapper_options):
        """Routes dispatcher"""
        self.controllers = {}
        self.mapper = routes.Mapper(**mapper_options)
        self.mapper.controller_scan = self.controllers.keys

    def connect(self, name, route, controller, **kwargs):
        self.controllers[name] = controller
        self.mapper.connect(name, route, controller=name, **kwargs)


    def match(self, request, path_info):
        """Find the right page handler."""

        result = self.mapper.match(path_info)

        if not result:
            # action, handler
            return None, None

        request.route = result
        params = result.copy()
        params.pop('controller', None)
        params.pop('action', None)
      
        handler = None
        controller = result.get('controller')
        controller = self.controllers.get(controller, controller)
        if controller:
            if isinstance(controller, classtype):
                controller = controller()

        action = result.get('action')
        if action is not None:
            handler = getattr(controller, action, None)
        else:
            handler = controller

        if request.method == 'GET':
            reqparams = request.GET.copy() 
        elif request.method != 'HEAD':
            reqparams = request.POST.copy()
        else:
            reqparams = {}

        reqparams.update(params)

        handler = PageHandler(handler, **reqparams)

        return action, handler



class PageHandler(object):

    """Callable which sets response.body."""

    def __init__(self, callable, *args, **kwargs):
        self.callable = callable
        self.kwargs = kwargs
        self.args = args

    def __call__(self):
        try:
            return self.callable(*self.args, **self.kwargs)
        except TypeError:
            x = exc_info()[1]
            try:
                test_callable_spec(self.callable, self.args, self.kwargs)
            except exc.HTTPException:
                raise exc_info()[1]
            except:
                raise x
            raise


def test_callable_spec(callable, callable_args, callable_kwargs, show_mismatched_params=True):
    """
    Inspect callable and test to see if the given args are suitable for it.

    When an error occurs during the handler's invoking stage there are 2
    erroneous cases:
    1.  Too many parameters passed to a function which doesn't define
        one of *args or **kwargs.
    2.  Too little parameters are passed to the function.

    There are 3 sources of parameters to a cherrypy handler.
    1.  query string parameters are passed as keyword parameters to the
        handler.
    2.  body parameters are also passed as keyword parameters.
    3.  when partial matching occurs, the final path atoms are passed as
        positional args.
    Both the query string and path atoms are part of the URI.  If they are
    incorrect, then a 404 Not Found should be raised. Conversely the body
    parameters are part of the request; if they are invalid a 400 Bad Request.
    """
    try:
        (args, varargs, varkw, defaults) = inspect.getargspec(callable)
    except TypeError:
        if isinstance(callable, object) and hasattr(callable, '__call__'):
            (args, varargs, varkw,
             defaults) = inspect.getargspec(callable.__call__)
        else:
            # If it wasn't one of our own types, re-raise
            # the original error
            raise

    if args and args[0] == 'self':
        args = args[1:]

    arg_usage = dict([(arg, 0,) for arg in args])
    vararg_usage = 0
    varkw_usage = 0
    extra_kwargs = set()

    for i, value in enumerate(callable_args):
        try:
            arg_usage[args[i]] += 1
        except IndexError:
            vararg_usage += 1

    for key in callable_kwargs.keys():
        try:
            arg_usage[key] += 1
        except KeyError:
            varkw_usage += 1
            extra_kwargs.add(key)

    # figure out which args have defaults.
    args_with_defaults = args[-len(defaults or []):]
    for i, val in enumerate(defaults or []):
        # Defaults take effect only when the arg hasn't been used yet.
        if arg_usage[args_with_defaults[i]] == 0:
            arg_usage[args_with_defaults[i]] += 1

    missing_args = []
    multiple_args = []
    for key, usage in arg_usage.items():
        if usage == 0:
            missing_args.append(key)
        elif usage > 1:
            multiple_args.append(key)

    if missing_args:
        # In the case where the method allows body arguments
        # there are 3 potential errors:
        # 1. not enough query string parameters -> 404
        # 2. not enough body parameters -> 400
        # 3. not enough path parts (partial matches) -> 404
        #
        # We can't actually tell which case it is,
        # so I'm raising a 404 because that covers 2/3 of the
        # possibilities
        #
        # In the case where the method does not allow body
        # arguments it's definitely a 404.
        message = None
        if show_mismatched_params:
            message = "Missing parameters: %s" % ",".join(missing_args)
            raise exc.HTTPNotFound(message)

    # the extra positional arguments come from the path - 404 Not Found
    if not varargs and vararg_usage > 0:
        raise exc.HTTPNotFound()

    body_params = serving.request.params or {}
    body_params = set(body_params.keys())
    qs_params = set(callable_kwargs.keys()) - body_params

    if multiple_args:
        message = None
        if show_mismatched_params:
            message = "Multiple values for parameters: "\
                "%s" % ",".join(multiple_args)
        if qs_params.intersection(set(multiple_args)):
            # If any of the multiple parameters came from the query string then
            # it's a 404 Not Found
            raise exc.HTTPNotFound(message)
        else:
            # Otherwise it's a 400 Bad Request
            raise exc.HTTPBadRequest(message)


    if not varkw and varkw_usage > 0:

        # If there were extra query string parameters, it's a 404 Not Found
        extra_qs_params = set(qs_params).intersection(extra_kwargs)
        if extra_qs_params:
            message = None
            if show_mismatched_params:
                message = "Unexpected query string "\
                    "parameters: %s" % ", ".join(extra_qs_params)
            raise exc.HTTPNotFound(message)

        # If there were any extra body parameters, it's a 400 Not Found
        extra_body_params = set(body_params).intersection(extra_kwargs)
        if extra_body_params:
            message = None
            if show_mismatched_params:
                message = "Unexpected body parameters: "\
                    "%s" % ", ".join(extra_body_params)
            raise exc.HTTPBadRequest(message)