from solo.web.asset import AssetController
from solo.web.asset import FileIter, FileIterator
import unittest
from webob import exc
import os.path
from solo.web.ctx import serving
from solo.web.app import App
from webob import Request


class AssetTest(unittest.TestCase):

    def setUp(self):
        self.asset = AssetController(os.path.join(os.path.dirname(__file__), 'assets'), 'index.html')

    def test_get_content_type(self):
        self.assertEqual(self.asset.get_content_type('assets/index.html'), 'text/html')
        self.assertEqual(self.asset.get_content_type('assets/dummy'), 'application/octet-stream')

    def test_get_absolute_path(self):
        path = self.asset.get_absolute_path(self.asset.root, 'index.html')
        self.assertIn('assets/index.html'.replace('/', os.path.sep), path)

        path = self.asset.get_absolute_path(self.asset.root, 'dummy_dir/dummy')
        self.assertIn('assets/dummy_dir/dummy'.replace('/', os.path.sep), path)

    def test_check_absolute_path(self):

        self.assertTrue(self.asset.check_absolute_path(self.asset.root, self._path('dummy/')).endswith('dummy'))
        self.assertTrue(self.asset.check_absolute_path(self.asset.root, self._path('dummy')).endswith('dummy'))
        self.assertRaises(exc.HTTPNotFound, lambda:
                          self.asset.check_absolute_path(self.asset.root, self._path('not_exist')))

        class DummyRequest(object):
            path_info = 'no_end_with_slash'
        serving.request = DummyRequest()
        self.assertRaises(exc.HTTPSeeOther, lambda:
                          self.asset.check_absolute_path(self.asset.root, self._path('dummy_dir')))

    def _path(self, path):
        return self.asset.get_absolute_path(self.asset.root, path)


class FileIteratorTest(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), 'assets', 'index.html')

    def test_iter(self):
        fileiter = FileIterator(self.path, None, None, 6)
        self.assertEqual('Hello ', next(fileiter))
        self.assertEqual('Asset!', next(fileiter))
        self.assertRaises(StopIteration, lambda: next(fileiter))

    def test_start(self):
        fileiter = FileIterator(self.path, 2, None, 2)
        self.assertEqual('ll', next(fileiter))

    def test_strat_and_stop(self):
        fileiter = FileIterator(self.path, 2, 5, 2)
        self.assertEqual('ll', next(fileiter))
        self.assertEqual('o', next(fileiter))
        self.assertRaises(StopIteration, lambda: next(fileiter))


class FileFileIterTest(unittest.TestCase):

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), 'assets', 'index.html')

    def test_iter(self):
        fileiter = FileIter(self.path, None, None, 6)
        self.assertEqual('Hello ', next(fileiter))
        self.assertEqual('Asset!', next(fileiter))
        self.assertRaises(StopIteration, lambda: next(fileiter))

    def test_start(self):
        fileiter = FileIter(self.path, 2, None, 2)
        self.assertEqual('ll', next(fileiter))

    def test_start_and_stop(self):
        fileiter = FileIter(self.path, 2, 5, 2)
        self.assertEqual('ll', next(fileiter))
        self.assertEqual('o', next(fileiter))
        self.assertRaises(StopIteration, lambda: next(fileiter))

    def test_app_iter_range(self):
        fileiter = FileIter(self.path, block_size=2)
        app_iter = fileiter.app_iter_range(2, 5)
        self.assertEqual('ll', next(app_iter))
        self.assertEqual('o', next(app_iter))
        self.assertRaises(StopIteration, lambda: next(app_iter))


class AssetAppTest(unittest.TestCase):

    def setUp(self):
        self.app = App()
        path = os.path.join(os.path.dirname(__file__), 'assets')
        self.app.asset('asset', '/', path, 'index.html')

    def test_get(self):
        req = Request.blank('/index.html')
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, 'text/html')
        self.assertEqual(res.content_length, 12)
        self.assertEqual(res.body, 'Hello Asset!')

        # test vaild etag
        req = Request.blank('/index.html')
        req.if_none_match = res.etag
        res2 = req.get_response(self.app)
        self.assertEqual(res2.status_code, 304)

        # test last modified
        req = Request.blank('/index.html')
        req.if_modified_since = res.last_modified
        res3 = req.get_response(self.app)
        self.assertEqual(res3.status_code, 304)

        # invaild etag
        req = Request.blank('/index.html')
        req.if_range = 'invalid etag'
        req.range = (6, 12)
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_length, 12)
        self.assertEqual(res.body, 'Hello Asset!')

    def test_head(self):
        req = Request.blank('/index.html')
        req.method = 'HEAD'
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, 'text/html')
        self.assertEqual(res.body, '')

        # test etag
        req = Request.blank('/index.html')
        req.method = 'HEAD'
        req.if_none_match = res.etag
        res2 = req.get_response(self.app)
        self.assertEqual(res2.status_code, 304)

        # invaild etag
        req = Request.blank('/index.html')
        req.if_range = 'invalid etag'
        req.range = (6, 12)
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_length, 12)
        self.assertEqual(res.body, 'Hello Asset!')

    def test_range(self):
        req = Request.blank('/index.html')
        req.range = (6, 12)
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 206)
        self.assertEqual(res.content_type, 'text/html')
        self.assertEqual(res.body, 'Asset!')
        self.assertEqual(res.headers['Content-Range'], 'bytes 6-11/12')

        # valid  etag
        req = Request.blank('/index.html')
        req.if_range = res.etag
        req.range = (6, 12)
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 206)
        self.assertEqual(res.content_type, 'text/html')
        self.assertEqual(res.body, 'Asset!')
        self.assertEqual(res.headers['Content-Range'], 'bytes 6-11/12')

        # invaild etag
        req = Request.blank('/index.html')
        req.if_range = 'invalid etag'
        req.range = (6, 12)
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_length, 12)
        self.assertEqual(res.body, 'Hello Asset!')

    def test_not_found(self):
        req = Request.blank('/not_found')
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 404)

    def test_redirect(self):
        req = Request.blank('/dummy_dir')
        res = req.get_response(self.app)
        self.assertEqual(res.status_code, 303)
        self.assertEqual(res.status, '303 See Other')
        self.assertEqual(res.location, 'http://localhost/dummy_dir/')


if __name__ == '__main__':
    unittest.main()