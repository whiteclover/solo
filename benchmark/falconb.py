import falcon

class ThingsResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = ("Hello World")

app = falcon.API()

things = ThingsResource()

app.add_route('/', things)

if __name__ == '__main__':
    from gevent.wsgi import WSGIServer
    http_server = WSGIServer(('', 8080), app, log=None)
    http_server.serve_forever()
