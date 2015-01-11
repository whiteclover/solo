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


"""
Flash messaging system for sending info to the user in a non-obtrusive way
"""

import sys

# True if we are running on Python 3.
PY3 = sys.version_info[0] == 3

if PY3: # pragma: no cover
    unicode_text = str
    from urllib.parse import unquote as url_unquote
    from urllib.parse import quote as url_quote
else:
    unicode_text = unicode
    from urllib import unquote as url_unquote
    from urllib import quote as url_quote


from solo.util import json_decode,json_encode
from solo.web.ctx import response, request

import logging

log = logging.getLogger(__name__)


from markupsafe import escape_silent as escape


class Flash(object):
    """
    Flash Message Creator
    """
    template = '<div id="%(container_id)s">'\
               '<script type="text/javascript">'\
               '//<![CDATA[\n'\
               '%(js_code)s'\
               '%(js_call)s'\
               '\n//]]>'\
               '</script>'\
               '</div>'

    static_template = '<div id="%(container_id)s">'\
                      '<div class="%(status)s">%(message)s</div>'\
                      '</div>'

    js_code = '''if(!window.webflash){webflash=(function(){var j=document;var k=j.cookie;var f=null;var e=false;\
var g=null;var c=/msie|MSIE/.test(navigator.userAgent);var a=function(m){return j.createTextNode(m.message)};\
var l=function(n,m){};var b=function(o,m){var n=m;if(typeof(o)=="string"){n=window[o]}\
else{if(o){n=o}}return n};var h=function(){var p=k.indexOf(f+"=");if(p<0){return null}\
var o=p+f.length+1;var m=k.indexOf(";",o);if(m==-1){m=k.length}var n=k.substring(o,m);\
j.cookie=f+"=; expires=Fri, 02-Jan-1970 00:00:00 GMT; path=/";return webflash.lj(unescape(n))};\
var i=function(){if(e){return}e=true;var p=h();if(p!==null){var m=j.getElementById(g);\
var n=j.createElement("div");if(p.status){n.setAttribute(c?"className":"class",p.status)}\
var o=a(p);n.appendChild(o);m.style.display="block";if(p.delay){setTimeout(function(){m.style.display="none"},p.delay)}\
m.appendChild(n);l(p,m)}};var d=function(){if(!c){var m="DOMContentLoaded";\
j.addEventListener(m,function(){j.removeEventListener(m,arguments.callee,false);i()},false);\
window.addEventListener("load",i,false)}else{if(c){var m="onreadystatechange";\
j.attachEvent(m,function(){j.detachEvent(m,arguments.callee);i()});\
if(j.documentElement.doScroll&&!frameElement){(function(){if(e){return}try{j.documentElement.doScroll("left")}\
catch(n){setTimeout(arguments.callee,0);return}i()})()}window.attachEvent("load",i)}}};\
return function(m){f=m.name||"webflash";g=m.id||"webflash";l=b(m.on_display,l);a=b(m.create_node,a);\
return{payload:h,render:d}}})();webflash.lj=function(s){var r;eval("r="+s);return r}};'''

    def __init__(self, cookie_name="webflash", default_status="ok"):
        self.default_status = default_status
        self.cookie_name = cookie_name

    def __call__(self, message, status=None, **extra_payload):
        # Force the message to be unicode so lazystrings, etc... are coerced
        message = unicode_text(message)

        payload = self.prepare_payload(message = message,
                                       status = status or self.default_status,
                                       **extra_payload)

        if request is not None:
            # Save the payload in environ too in case JavaScript is not being
            # used and the message is being displayed in the same request.
            request.environ['webflash.payload'] = payload

        response.set_cookie(self.cookie_name, payload)
        if len(response.headers['Set-Cookie']) > 4096:
            raise ValueError('Flash value is too long (cookie would be >4k)')

    def prepare_payload(self, **data):
        return url_quote(json_encode(data))

    def js_call(self, container_id):
        return 'webflash(%(options)s).render();' % {'options': json_encode({'id': container_id,
                                                                           'name': self.cookie_name})}

    def render(self, container_id, use_js=True):
        if use_js:
            return self._render_js_version(container_id)
        else:
            return self._render_static_version(container_id)

    def _render_static_version(self, container_id):
        payload = self.pop_payload()
        if not payload:
            return ''
        payload['message'] = escape(payload.get('message',''))
        payload['container_id'] = container_id
        return self.static_template % payload

    def _render_js_version(self, container_id):
        return self.template % {'container_id': container_id,
                                'js_code': self.js_code,
                                'js_call': self.js_call(container_id)}

    def pop_payload(self):
        # First try fetching it from the request
        payload = request.environ.get('webflash.payload', {})
        if not payload:
            payload = request.cookies.get(self.cookie_name, {})

        if payload:
            payload = json_decode(url_unquote(payload))
            if 'webflash.deleted_cookie' not in request.environ:
                response.delete_cookie(self.cookie_name)
                request.environ['webflash.delete_cookie'] = True
        return payload or {}

    @property
    def message(self):
        return self.pop_payload().get('message')

    @property
    def status(self):
        return self.pop_payload().get('status') or self.default_status


flash = Flash()
