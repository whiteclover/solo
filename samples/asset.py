from solo.web.app import App
from solo.web.server import WebServer
import os.path



class AssetApp(App):

    def initialize(self):
        root = os.path.join(os.path.dirname(__file__), "static")
        self.asset('static' ,'/', root,  default_filename='index.html')



if __name__ == '__main__':
    app = AssetApp('asset')
    WebServer(('127.0.0.1', 8080), app, log=None).start()