import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
from application.handlers import GroupHandler, AgentIndexHandler, AgentHandler, ResultHandler
from keyenv import get_api_key


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", IndexHandler),
            (r"/group", GroupHandler),
            (r"/agent/([^/]+)", AgentIndexHandler),
            (r"/agent/([^/]+)/train", AgentHandler),
            (r"/agent/([^/]+)/result", ResultHandler),
        ]
        settings = dict(
            cookie_secret=os.environ.get("SECRET_TOKEN", "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            debug=True,
            api_key=get_api_key()
        )

        data_dir = os.path.join(os.path.dirname(__file__), "../data/release")
        AgentHandler.load_brain(data_dir)

        tornado.web.Application.__init__(self, handlers, **settings)


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")
