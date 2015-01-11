
from solo.web.app import App
from solo.web.ctx import response
from solo.web.server import WebServer
from solo.template import setup_template, render_template, template_vars
from solo.web.flash import flash


class FlashController:

    def flash(self):
        flash('flash message', 'error')
        return render_template('flash.html')

    def flash_js(self):
        flash('flash_js message', 'error')
        return render_template('flash_js.html')


class FalshApp(App):

    def initialize(self):
        import os.path
        cur = os.path.dirname(__file__)
        template_vars['flash'] = flash.render
        setup_template([os.path.join(cur, 'view')])


        self.asset('static', '/static', os.path.join(cur, 'static'))


        ctl = FlashController()
        route = self.route()
        route.mapper.explicit = False
        route.connect('flash', '/flash', controller=ctl, action='flash', conditions=dict(method=["GET"]))
        route.connect('flash_js', '/flash_js', controller=ctl, action='flash_js', conditions=dict(method=["GET"]))




if __name__ == '__main__':
    app = FalshApp('flash')
    WebServer(('127.0.0.1', 8080), app, log=None).start()