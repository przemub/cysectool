# Bokeh runner
import tornado.web
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from bokeh.server.server import Server

from src import visualiser, api

server = Server({'/visualiser': Application(FunctionHandler(visualiser.main))},
                extra_patterns=[('/api', api.ApiHandler),
                                (r'/my_static/(.*)', tornado.web.StaticFileHandler, {"path": "my_static/"})])
server.start()

if __name__ == '__main__':
    print('Opening Tornado app with embedded Bokeh application on http://localhost:5006/')

    server.io_loop.start()
