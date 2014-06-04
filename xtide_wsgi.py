#!/usr/bin/env python
#
#  This
#   file
#    is
#     not
#      used
#
#  It's just sitting around in case I ever make an xtide JSON service.
#

from cgi import parse_qs
import gevent
from gevent.pool import Pool
from gevent import wsgi
import json
import xtide

p = Pool(8)

def run_xtide(*args, **kwargs):
    return p.apply(xtide.run_xtide, args = args, kwds = kwargs)

def application(env, start_response):
    param = parse_qs(env.get('QUERY_STRING', ''))

    start_response('200 OK', [('Content-type', 'application/json')])

    if 'site' in param:
        site = param['site'][0]
    else:
        return json.dumps({ 'status': 'ERROR', 'data': 'Site not specified' })

    def param_or_none(p): return param[p][0] if p in param else None
    def param_to_arg(p):
        if p in param: arg[p] = param[p][0]

    arg = {}
    start_time = param_or_none('start_time')
    stop_time = param_or_none('stop_time')
    param_to_arg('target')
    param_to_arg('target2')

    try:
        # ret1 = xtide.run_xtide(site, start_time, stop_time)
        ret1 = run_xtide(site, start_time, stop_time)
        if 'site2' in param:
            # levels2 = xtide.run_xtide(param['site2'][0], start_time, stop_time)
            levels2 = run_xtide(param['site2'][0], start_time, stop_time)
            arg['levels2'] = levels2
            
        spans = xtide.target_spans(ret1, **arg)
    except Exception as e:
        return json.dumps({ 'status': 'ERROR', 'data': str(e) })

    return json.dumps({ 'status': 'OK', 'data': spans })

http_server = wsgi.WSGIServer(('', 6069), application)
http_server.serve_forever()
