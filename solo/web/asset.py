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
import mimetypes
import os
import os.path
from os.path import (
    getmtime,
    getsize
)
from webob import exc


from solo.web.ctx import request, response

LOGGER = logging.getLogger('asset')

_BLOCK_SIZE = 4096 * 64  # 256K


class AssetController(object):

    def __init__(self, root, default_filename=None, block_size=_BLOCK_SIZE):
        self.root = root
        self.default_filename = default_filename
        self.block_size = block_size or _BLOCK_SIZE

    def get_content_type(self, absolute_path):
        mine_type, encoding = mimetypes.guess_type(absolute_path)
        mine_type = mine_type or 'application/octet-stream'
        return mine_type

    def asset(self, path):
        if request.method == 'HEAD':
            return self.get(path, False)
        return self.get(path)

    def head(self, path):
        self.get(path, load=False)

    def get(self, path, load=True):
        LOGGER.info('request.path_info:%s', request.path_info)
        path = self.parse_url_path(path)
        absolute_path = self.get_absolute_path(self.root, path)
        absolute_path = self.check_absolute_path(self.root, absolute_path)
        if absolute_path is None:
            raise exc.HTTPNotFound('The asset file not found')

        # !!! must initialize the content type and set codintional response firstly
        response.content_type = self.get_content_type(absolute_path)
        response.conditional_response = True
        if load:
            response.app_iter = FileIter(absolute_path, block_size=self.block_size)

        last_modified, size = getmtime(absolute_path), getsize(absolute_path)
        response.last_modified = last_modified
        response.content_length = size
        response.etag = '%s-%s-%s' % (last_modified,
                                      size, hash(absolute_path))

    def parse_url_path(self, url_path):
        """Converts a asset URL PATH into a filesystem path."""
        if os.path.sep != "/":
            url_path = url_path.replace("/", os.path.sep)
        return url_path

    @classmethod
    def get_absolute_path(cls, root, path):
        abspath = os.path.abspath(os.path.join(root, path))
        return abspath

    def check_absolute_path(self, root, absolute_path):
        root = os.path.abspath(root)
        if not (absolute_path + os.path.sep).startswith(root):
            raise exc.HTTPNotFound("%s is not in root static directory" % (absolute_path))
        if (os.path.isdir(absolute_path) and self.default_filename is not None):

            if not request.path_info.endswith("/"):
                raise exc.HTTPSeeOther(location=request.path_info + "/")

            absolute_path = os.path.join(absolute_path, self.default_filename)

        if not os.path.exists(absolute_path):
            raise exc.HTTPNotFound('The %s asset is not found' % (absolute_path))
        if not os.path.isfile(absolute_path):
            raise exc.HTTPNotFound("%s is not in a file" % (absolute_path))
        return absolute_path


class FileIter(object):

    """ A fixed-block-size iterator for use as a WSGI app_iter.
    ``file`` is a Python file pointer (or at least an object with a ``read``
    method that takes a size hint).

    ``block_size`` is an optional block size for iteration."""

    def __init__(self, filename, start=None, stop=None, block_size=_BLOCK_SIZE):
        self.filename = filename
        self.start = start
        self.stop = stop
        self.block_size = block_size
        self.fileiterator = FileIterator(self.filename, self.start, self.stop, self.block_size)

    def __iter__(self):
        return self

    def next(self):
        return self.fileiterator.next()

    __next__ = next  # py3

    def app_iter_range(self, start, stop):
        return self.__class__(self.filename, start, stop, self.block_size)

    def close(self):
        self.fileiterator.close()


class FileIterator(object):

    def __init__(self, filename, start, stop, block_size):
        self.block_size = block_size
        self.filename = filename

        if start:
            self.fileobj.seek(start)

        self.length = (stop - start) if stop is not None else None

    @property
    def fileobj(self):
        if not hasattr(self, '_fileobj'):
            self._fileobj = open(self.filename, 'rb')
        return self._fileobj

    def __iter__(self):

        return self

    def next(self):
        if self.length is not None and self.length <= 0:
            raise StopIteration
        chunk = self.fileobj.read(self.block_size)
        if not chunk:
            raise StopIteration
        if self.length is not None:
            self.length -= len(chunk)
            if self.length < 0:
                # Chop off the extra:
                chunk = chunk[:self.length]
        return chunk

    __next__ = next  # py3 compat

    def close(self):
        if hasattr(self, '_fileobj'):
            self._fileobj.close()