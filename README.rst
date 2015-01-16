solo
#####

Web Framework Based Gevent & Webob & Routes


Benchmark
===========


ab  -n10000 -c500   http://localhost:8080/

Run in
Python 2.7.9
Intel(R) Core(TM) i7-3520M CPU @ 2.90GHz
8GB RAM

.. table:: 
    
   
    ============== ============ =========== ========== ============== 
    app            server       workers     requets    request/sec  
    ============== ============ =========== ========== ============== 
    bottle         gevent         500        10000     3623.53
    falcon         gevent         500        10000     4686.68
    tornado        tornado        500        10000     1315.57   
    flask          gevent         500        10000     2594.68
    django         gevent         500        10000     2668.52
    solo           gevent         500        10000     3532.94
    ============== ============ =========== ========== ============== 


The Projects use solo
======================

#. `Lilac (Distributed Scheduler Task System) <https://github.com/thomashuang/Lilac>`_

Hello
======

.. code-block:: python

    #!/usr/bin/env python

    from solo.web.server import WebServer
    from solo.web.app import App

    class HelloRoot(object):

        def index(self):
            return "Hello World!"

        def page(self, page):
            return page

    class HelloApp(App):

        def initialize(self):
            ctl = HelloRoot()
            route = self.route()
            route.mapper.explicit = False
            route.connect('index', '/', controller=ctl, action='index')
            route.connect('page', '/page/:page', controller=ctl, action='page')


    if __name__ == '__main__':
        app = HelloApp()
        WebServer(('127.0.0.1', 8080), app, log=None).start()


.. note:: more examples see `Lilac (Distributed Scheduler Task System) <https://github.com/thomashuang/Lilac>`_ or `samples <https://github.com/thomashuang/solo/tree/master/samples>`_ 

Requirement
===========

The modules are required to run solo as below:

#. gevent
#. webob
#. routes 
#. mako


How to install
==============

Firstly download or fetch it form github then run the command in shell:

.. code-block:: bash

    cd solo # the path to the project
    python setup.py install


Development
===========

Fork or download it, then run:

.. code-block:: bash 

    cd solo # the path to the project
    python setup.py develop



Compatibility
=============

Built and tested under Python 2.7 


LICENSE
=======

    Copyright (C) 2015 Thomas Huang

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 2 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
