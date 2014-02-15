#!/usr/bin/env python

from gevent import monkey
monkey.patch_all(subprocess=True)

from astral import Astral
import datetime
from gevent import wsgi
from htmlmin import minify
import re
#import time
from time import strftime, strptime, time, localtime, mktime
import urllib
import web

# Expects template to be named "*.html".
# from web.contrib.template import render_jinja

import xtide

foo = "bar"

urls = (
    '/', 'index',
    '/site', 'site',
    '/graph', 'graph',
)

class render_jinja:
    def __init__(self, *a, **kwargs):
        from jinja2 import Environment,FileSystemLoader
        self._lookup = Environment(loader=FileSystemLoader(*a, **kwargs),
                                   trim_blocks = True, lstrip_blocks = True)

    def __getattr__(self, name):
        path = name + '.djhtml'
        t = self._lookup.get_template(path)
        return t.render

render = render_jinja('templates')

class graph:
    def GET(self):
        i = web.input()

        start_time = None
        if "site" not in i: return "No site specified."
        if "time" in i: start_time = float(i.time)

        web.header('Content-Type', 'image/png')
        g = xtide.xtide_graph(i.site, start_time = start_time)
        return g

def format_time(seconds):
    return strftime("%l:%M %p", localtime(seconds))

def sunrise_sunset(this_time):
    a = Astral()
    city = a["San Francisco"]
    sun = city.sun(date=datetime.date(1,1,1).fromtimestamp(this_time),
                   local=True)
    sunrise_time = float(sun['sunrise'].strftime('%s'))
    sunset_time = float(sun['sunset'].strftime('%s'))
    return (sunrise_time, sunset_time)

class site:
    def GET(self):
        i = web.input()

        if "tide_site" not in i and "current_site" not in i:
            return "No sites specified."

        kwargs = {}

        if 'current_site' in i:
            kwargs['current_site'] = urllib.quote(i.current_site)
            kwargs['name'] = kwargs['current_site']
        if 'tide_site' in i:
            kwargs['tide_site'] = urllib.quote(i.tide_site)
            kwargs['name'] = kwargs['tide_site']
        if 'name' in i:
            kwargs['name'] = i.name

        try: target = float(i.target)
        except: target = 0.0
        try: this_time = float(i.time)
        except: this_time = time()

        (start_time, stop_time) = sunrise_sunset(this_time)

        # Helper function to preprocess tide spans before passing to
        # our template.
        def get_spans(site, target = 0.0, current = False):
            spans = xtide.target_spans(
                xtide.run_xtide(site, start_time = start_time,
                                stop_time = stop_time),
                target = target, now = True, maxima = current
            )
            spans[0]['first'] = True
            spans[len(spans)-1]['last'] = True

            for i, span in enumerate(spans):
                spans[i]['start'] = format_time(span['start'])
                spans[i]['end'] = format_time(span['end'])
                if 'now' in span:
                    spans[i]['now_tag'] = 'Now'
                    spans[i]['now'][0] = "%+.1f" % (span['now'][0])
                    spans[i]['now'][1] = format_time(span['now'][1])
                if 'maximum' in span:
                    spans[i]['maximum'][0] = "%+.1f" % (span['maximum'][0])
                    spans[i]['maximum'][1] = format_time(span['maximum'][1])

            return spans

        if "tide_site" in i:
            kwargs["tide_spans"] = get_spans(i.tide_site, target)
        if "current_site" in i:
            kwargs["current_spans"] = get_spans(i.current_site, current = True)

        kwargs.update({
            "this_day": strftime("%a %h %e", localtime(this_time)),
            "back_url": web.ctx.homepath,
            "url_notime": web.ctx.path + re.sub('&?time=[^&;]+', '',
                                                web.ctx.query),
            "time_yesterday": str(this_time - 86400),
            "date_yesterday": strftime(
                "%a %h %e", localtime(this_time - 86400)),
            "time_tomorrow": str(this_time + 86400),
            "date_tomorrow": strftime(
                "%a %h %e", localtime(this_time + 86400)),
            "graph_path": (web.ctx.homepath + '/graph?time=' + str(this_time))
        })

        return render.site(**kwargs)

class index:
    def GET(self):
        i = web.input()

        try: this_time = float(i.time)
        except: this_time = time()
        
        start_time = mktime(strptime
                            (strftime("%Y-%m-%d 14:00", localtime(this_time)),
                            "%Y-%m-%d %H:%M"))
        stop_time = mktime(strptime
                           (strftime("%Y-%m-%d 18:00", localtime(this_time)),
                            "%Y-%m-%d %H:%M"))

        def green_red_yellow(tide_site, current_site, state):
            if tide_site and current_site:
                if state == 0: return "red"
                if state == 1: return "green"
                return "yellow"
            if tide_site:
                return "green" if state else "red"
            if current_site:
                return "red" if state else "green"

        def box(tide_site = None, current_site = None, tag = None,
                target = None, name = None, url = None):
            thebox = {
                "site_url": '/site?time=%f&%s%s%s%s' % (
                    this_time,
                    "&name=%s" % urllib.quote(name) if name else "",
                    "&current_site=%s" % urllib.quote(current_site) if current_site else "",
                    "&tide_site=%s" % urllib.quote(tide_site) if tide_site else "",
                    "&target=%s" % urllib.quote(str(target)) if target else "",
                ),
                "tag": tag if tag else "F",
            }

            levels1 = None
            if tide_site:
                levels1 = xtide.run_xtide(tide_site, start_time=start_time, stop_time=stop_time)

            levels2 = None
            if current_site:
                levels2 = xtide.run_xtide(current_site, start_time=start_time, stop_time=stop_time)

            spans = []
            if levels1 and not levels2: spans = xtide.target_spans(levels1, target, now=True)
            if levels2 and not levels1: spans = xtide.target_spans(levels2, now=True)
            if levels2 and levels1: spans = xtide.target_spans(levels1, target, levels2, now=True)
            if not levels1 and not levels2: raise Exception("No sites specified.")

            thebox['color'] = "yellow"
            if len(spans) == 1:
                thebox['color'] = green_red_yellow(tide_site, current_site, spans[0]['state'])

            bars = []
            total_time = float(spans[len(spans)-1]['end'] - spans[0]['start'])
            bar_width = float(110)
            left = 0
            for span in spans:
                bar = { "left": str(left) }
                width = "%.0f" % ((span['end'] - span['start']) / total_time * bar_width)
                left += int(width)
                bar['width'] = width
                bar['color'] = green_red_yellow(tide_site, current_site, span['state'])

                if 'now' in span:
                    nowleft = (span['now'][1] - spans[0]['start']) / total_time * bar_width - 3
                    print 'now'
                    thebox['now'] = "%.0f" % (nowleft)

                bars.append(bar)
            bars[0]['first'] = ' first'
            bars[len(bars)-1]['last'] = ' last'

            if len(spans) > 1 or thebox['color'] == "yellow":
                thebox['bars'] = bars

            return thebox

        web.header('Cache-Control', ('no-store, no-cache, must-revalidate,' +
                                     'post-check=0, pre-check=0'))

        boxes = []
        boxes.append(render.box({
            "box": box('Oyster Point Marina', tag='Ha', name='Haskins', target=3.25)}))
        boxes.append(render.box({
            "box": box(current_site = 'San Francisco Bay Entrance', tag='GG', name='Golden Gate')}))
        boxes.append(render.box({
            "box": box(current_site = 'Treasure Island .5 mi N', tag='TI',
                       name='Treasure Island')}))
        boxes.append(render.box({
            "box": box('San Mateo Bridge (West)', 'San Mateo Bridge, South',
                       name='3rd Ave', tag='3rd', target=2.0)}))
        boxes.append(render.box({
            "box": box('Palo Alto', 'Dumbarton Bridge, San Francisco Bay, California Current',
                       tag='PA', name='Palo Alto', target=4.0)}))
        boxes.append(render.box({
            "box": box(current_site = 'Sherman Island (East)', tag='&Delta;',
                       name='Sherman Island')}))

        kwargs = {
            "boxes": boxes,
            "this_day": strftime("%a %h %e", localtime(this_time)),
            "url_notime": web.ctx.path + re.sub('&?time=[^&;]+', '',
                                                web.ctx.query),
            "time_yesterday": str(this_time - 86400),
            "date_yesterday": strftime(
                "%a %h %e", localtime(this_time - 86400)),
            "time_tomorrow": str(this_time + 86400),
            "date_tomorrow": strftime(
                "%a %h %e", localtime(this_time + 86400)),
        }
        
        return render.tides(**kwargs)

if __name__ == "__main__":
    #web.application(urls, globals()).run()
    app = web.application(urls, globals()).wsgifunc()
    app = web.httpserver.StaticMiddleware(app)
    http_server = wsgi.WSGIServer(('', 8080), app)
    http_server.serve_forever()
