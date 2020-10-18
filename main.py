# Bokeh runner
import tornado.web
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.server.server import Server

from src import visualiser, api, edit


def run_server():
    server = Server(
        {"/visualiser": Application(FunctionHandler(visualiser.main))},
        extra_patterns=[
            ("/api", api.ApiHandler),
            ("/edit", edit.EditHandler),
            ("/ping", api.PingHandler),
            (r"/my_static/(.*)", tornado.web.StaticFileHandler, {"path": "my_static/"}),
        ],
        allow_websocket_origin=[
            "hegel.eecs.qmul.ac.uk:5006",
            "attackgraphs.eecs.qmul.ac.uk",
            "localhost:5006",
        ],
    )
    server.start()
    server.io_loop.start()


if __name__ == "__main__":
    print(
        "Opening Tornado app with embedded Bokeh application "
        "on http://localhost:5006/"
    )
    run_server()
