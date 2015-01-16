from gevent import monkey
monkey.patch_all()
from bottle import Bottle

app = Bottle()
@app.route('/')
def index():
    return "Hello World!"

if __name__ == '__main__':
    from gevent.wsgi import WSGIServer
    http_server = WSGIServer(('', 8080), app, log=None)
    http_server.serve_forever()
