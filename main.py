# Bokeh runner
from bokeh.server.server import Server

from src import visualiser, api

server = Server({'/visualiser': visualiser.main}, extra_patterns=[('/api', api.ApiHandler)])
server.start()

if __name__ == '__main__':
    print('Opening Tornado app with embedded Bokeh application on http://localhost:5006/')

    server.io_loop.start()
