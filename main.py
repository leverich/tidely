#!/usr/bin/env python
from gevent import monkey
monkey.patch_all(subprocess=True)

from gevent import wsgi
import web

import index
import graph
import detail

urls = (
    '/site', 'detail.detail',
    '/graph', 'graph.graph',
    '/', 'index.index',
)

app = web.application(urls, globals()).wsgifunc()
app = web.httpserver.StaticMiddleware(app)

if __name__ == "__main__":
    #web.application(urls, globals()).run()
    http_server = wsgi.WSGIServer(('', 8080), app)
    http_server.serve_forever()
