#!/usr/bin/env python

from astral import Astral
import datetime
import os
import re
import sys
from time import strftime, strptime, time, localtime, mktime
import urllib
import web
from web.contrib.template import render_jinja

curdir = os.path.dirname(__file__)
if curdir not in sys.path: sys.path.append(curdir)

import xtide

render = render_jinja(curdir + '/templates')

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

def get_spans(site, target = 0.0, current = False, start_time = None, stop_time = None):
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

class detail:
    def GET(self):
        i = web.input()

        if "tide_site" not in i and "current_site" not in i:
            return "No sites specified."

        kwargs = {}

        if 'current_site' in i:
            kwargs['current_site'] = urllib.quote(i.current_site)
            kwargs['name'] = i.current_site
        if 'tide_site' in i:
            kwargs['tide_site'] = urllib.quote(i.tide_site)
            kwargs['name'] = i.tide_site
        if 'name' in i:
            kwargs['name'] = i.name

        try: target = float(i.target)
        except: target = 0.0
        try: this_time = float(i.time)
        except: this_time = time()

        (start_time, stop_time) = sunrise_sunset(this_time)

        if "tide_site" in i:
            kwargs["tide_spans"] = get_spans(i.tide_site, target, start_time = start_time, stop_time = stop_time)
        if "current_site" in i:
            kwargs["current_spans"] = get_spans(i.current_site, current = True, start_time = start_time, stop_time = stop_time)

        url_notime = '?' + '&'.join([f for f in web.ctx.query[1:].split('&') if f[0:4] != 'time'])

        kwargs.update({
            "this_day": strftime("%a %h %e", localtime(this_time)),
            "back_url": web.ctx.homepath,
            "url_notime": url_notime,
            "time_yesterday": str(this_time - 86400),
            "date_yesterday": strftime(
                "%a %h %e", localtime(this_time - 86400)),
            "time_tomorrow": str(this_time + 86400),
            "date_tomorrow": strftime(
                "%a %h %e", localtime(this_time + 86400)),
            "graph_path": ('graph?time=' + str(this_time))
        })

        return render.detail(**kwargs)

