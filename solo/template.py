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

from mako.lookup import TemplateLookup

template_vars = {
    
}


def get_template(path):
    return _g_lookup.get_templte(path)


def new_templatelookup(directories, filesystem_checks=True, module_directory=None):
    lookup = TemplateLookup(directories=directories, filesystem_checks=True,
                module_directory=module_directory, 
                input_encoding='utf-8', output_encoding='utf-8', encoding_errors='replace')
    return lookup


def setup_template(directories, cache=False, module_cache_dir=None):
    global _g_lookup
    _g_lookup = new_templatelookup(directories, filesystem_checks=True, module_directory=None)


def render_template(path, **kwargs):
    kwargs.update(template_vars)
    return _g_lookup.get_template(path).render(**kwargs)
