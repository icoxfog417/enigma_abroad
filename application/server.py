import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import os.path
from application.handlers import GroupHandler, AgentIndexHandler, AgentHandler, ResultHandler


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
        )
        data_path = os.path.join(os.path.dirname(__file__), "../data/salons.json")
        model_path = os.path.join(os.path.dirname(__file__), "../data/salon_doc_edited_model.gensim")
        AgentHandler.load_brain(data_path, model_path)

        tornado.web.Application.__init__(self, handlers, **settings)


class IndexHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("index.html")
