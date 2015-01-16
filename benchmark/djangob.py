import sys
from django.core.wsgi import get_wsgi_application

"""
Settings
========
Would normally go in project_app/settings.py
"""
from django.conf import settings

settings.configure(
    DEBUG = True,
    SECRET_KEY = 'yourrandomsecretkey',
    ROOT_URLCONF = __name__,
    MIDDLEWARE_CLASSES = (
        'django.middleware.common.CommonMiddleware',
    ),
)

"""
Views
=====
Would normally go in app/views.py
"""
from django.http import HttpResponse

def index(request):
    return HttpResponse('Hello World')

"""
URLs
====
The root URL config normally goes in project_app/urls.py
"""
from django.conf.urls import url

urlpatterns = (
    url(r'^$', index),
)

"""
Manage.py
=========
Some setup code typically found in manage.py
"""

app = get_wsgi_application()

if __name__ == '__main__':
    from gevent.wsgi import WSGIServer
    http_server = WSGIServer(('', 8080), app, log=None)
    http_server.serve_forever()
