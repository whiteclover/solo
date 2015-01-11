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

from argparse import ArgumentParser


class Options(object):

    def __init__(self, help_doc):
        self.argparser = ArgumentParser(help_doc)

    def group(self, help_doc):
        group_parser =  self.argparser.add_argument_group(help_doc)
        return GroupOptions(group_parser)

    @property
    def define(self):
       return  self.argparser.add_argument

    def parse_args(self):
        return self.argparser.parse_args()


class GroupOptions(object):
    def __init__(self, group_parser):
        self.group_parser = group_parser

    @property
    def define(self):
        return self.group_parser.add_argument

_options = None
def setup_options(doc):
    global _options
    _options = Options(doc)

def group(help_doc):
    return _options.group(help_doc)


def define(*args, **kw):
    return _options.define(*args, **kw)

def parse_args():
    return _options.parse_args()