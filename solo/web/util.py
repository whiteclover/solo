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

from functools import wraps
from solo.web.ctx import response

from solo.util import json_encode

def jsonify(f):
    """The decorator will set response content type to application/json; charset=UTF-8,
    and als handle the object which has as_json method"""
    @wraps(f)
    def __(*args, **kwargs):
        response.content_type = 'application/json; charset=UTF-8'
        return json_encode(f(*args, **kwargs))

    return __