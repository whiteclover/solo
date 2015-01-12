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
from sys import exc_info
from webob import exc

LOGGER = logging.getLogger('solo.hook')

class Hook(object):

    """A callback and its metadata: failsafe, priority, and kwargs."""

    callback = None
    """
    The bare callable that this Hook object is wrapping, which will
    be called when the Hook is called."""

    failsafe = False
    """
    If True, the callback is guaranteed to run even if other callbacks
    from the same call point raise exceptions."""

    priority = 50
    """
    Defines the order of execution for a list of Hooks. Priority numbers
    should be limited to the closed interval [0, 100], but values outside
    this range are acceptable, as are fractional values."""

    kwargs = {}
    """
    A set of keyword arguments that will be passed to the
    callable on each call."""

    def __init__(self, callback, failsafe=None, priority=None, **kwargs):
        self.callback = callback

        if failsafe is None:
            failsafe = getattr(callback, "failsafe", False)
        self.failsafe = failsafe

        if priority is None:
            priority = getattr(callback, "priority", 50)
        self.priority = priority

        self.kwargs = kwargs

    def __lt__(self, other):
        # Python 3
        return self.priority < other.priority

    def __cmp__(self, other):
        # Python 2
        return cmp(self.priority, other.priority)

    def __call__(self):
        """Run self.callback(**self.kwargs)."""
        return self.callback(**self.kwargs)

    def __repr__(self):
        cls = self.__class__
        return ("%s.%s(callback=%r, failsafe=%r, priority=%r, %s)"
                % (cls.__module__, cls.__name__, self.callback,
                   self.failsafe, self.priority,
                   ", ".join(['%s=%r' % (k, v)
                              for k, v in self.kwargs.items()])))


class HookMap(dict):

    """A map of call points to lists of callbacks (Hook objects)."""

    def __new__(cls, points=None):
        d = dict.__new__(cls)
        for p in points or []:
            d[p] = []
        return d

    def __init__(self, *a, **kw):
        pass

    def attach(self, point, callback, failsafe=None, priority=None, **kwargs):
        """Append a new Hook made from the supplied arguments."""
        if point not in self:
            self[point] = []
        self[point].append(Hook(callback, failsafe, priority, **kwargs))
        self[point].sort()

    def run(self, point):
        """Execute all registered Hooks (callbacks) for the given point."""
        exc = None
        hooks = self.get(point, [])
        for hook in hooks:
            # Some hooks are guaranteed to run even if others at
            # the same hookpoint fail. We will still log the failure,
            # but proceed on to the next hook. The only way
            # to stop all processing from one of these hooks is
            # to raise SystemExit and stop the whole server.
            if exc is None or hook.failsafe:
                try:
                    hook()
                except (KeyboardInterrupt, SystemExit):
                    raise
                except (exc.HTTPRedirection, exc.HTTPException):
                    exc = exc_info()[1]
                except:
                    exc = exc_info()[1]
                    LOGGER.exception("Hook Error: %s", exc)
        if exc:
            raise exc

    def __copy__(self):
        newmap = self.__class__()
        # We can't just use 'update' because we want copies of the
        # mutable values (each is a list) as well.
        for k, v in self.items():
            newmap[k] = v[:]
        return newmap
    copy = __copy__

    def __repr__(self):
        cls = self.__class__
        return "%s.%s(points=%r)" % (
            cls.__module__,
            cls.__name__,
            copykeys(self)
        )
