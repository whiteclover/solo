

import unittest
from webob import exc
import os.path
from solo.web.ctx import serving, response
from solo.web.app import App
from webob import Request
from solo.util import json_encode

from solo.web.util import jsonify


class AppTest(unittest.TestCase):

    def setUp(self):
        self.app = App()

        class Hello():

            def index(self):
                return 'index'

            def internal_error(self):
                raise Exception('internal_error')

            @jsonify
            def json(self):
                return {'test': 'json'}

        menu = self.app.route()
        ctl = Hello()
       	menu.connect('index', '/', controller=ctl, action='index', conditions=dict(method=["GET"]))
        menu.connect('index1', '/index', controller=ctl, action='index', conditions=dict(method=["GET"]))
        menu.connect('json', '/json', controller=ctl, action='json', conditions=dict(method=["GET"]))
        menu.connect('internal_error', '/internal_error', controller=ctl, action='internal_error', conditions=dict(method=["GET"]))



    def test_app_name(self):
        self.assertEqual(self.app.name, 'Lilac')

    def test_index(self):
        req = Request.blank('/')
        res = req.get_response(self.app)
        self.assertEqual(res.body, 'index')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, 'text/html')

        req = Request.blank('/index')
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.body, 'index')
        self.assertEqual(res.content_type, 'text/html')

    def test_not_fonud(self):
        req = Request.blank('/not_found')
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 404)

    def test_internal_error(self):
        req = Request.blank('/internal_error')
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 500)
        self.assertIn('internal_error', res.body)

    def test_json(self):
        req = Request.blank('/json')
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 200)
        self.assertIn('json', res.body)
        self.assertEqual(res.content_type, 'application/json')


class TestJsonify(unittest.TestCase):

    def test_as_json(self):

        class Dummy(object):

            def as_json(self):
                return [1, 3, 3]

        self.assertEqual(json_encode(Dummy()), '[1, 3, 3]')

    def test_josnify(self):
        class DummpyResonse(object):
            pass

        serving.response = DummpyResonse()
        @jsonify
        def j():
            return {'json': 'test'}
       
        content = j()
        self.assertIn('json', content)
        self.assertEqual(response.content_type, 'application/json; charset=UTF-8')


if __name__ == '__main__':
    unittest.main(verbosity=2)