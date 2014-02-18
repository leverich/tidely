#!/usr/bin/env python

import os
import sys
import web

curdir = os.path.dirname(__file__)
if curdir not in sys.path: sys.path.append(curdir)

import index
import graph
import detail

urls = (
    '/site', 'detail.detail',
    '/graph', 'graph.graph',
    '/', 'index.index',
)

application = web.application(urls, globals()).wsgifunc()
application = web.httpserver.StaticMiddleware(application)

if __name__ == "__main__":
    web.application(urls, globals()).run()
    #from gevent import wsgi, monkey
    #monkey.patch_all(subprocess=True)
    #http_server = wsgi.WSGIServer(('', 8080), application)
    #http_server.serve_forever()
