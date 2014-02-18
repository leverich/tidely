#!/usr/bin/env python

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
        target = None, name = None, url = None, this_time = None):
    this_time = this_time if this_time else time()
    start_time = mktime(strptime(strftime("%Y-%m-%d 14:00", localtime(this_time)), "%Y-%m-%d %H:%M"))
    stop_time = mktime(strptime(strftime("%Y-%m-%d 18:00", localtime(this_time)), "%Y-%m-%d %H:%M"))

    thebox = {
        "site_url": 'site?time=%f%s%s%s%s' % (
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
            thebox['now'] = "%.0f" % (nowleft)

        bars.append(bar)
        bars[0]['first'] = ' first'
        bars[len(bars)-1]['last'] = ' last'

    if len(spans) > 1 or thebox['color'] == "yellow":
        thebox['bars'] = bars

    return thebox


class index:
    def GET(self):
        i = web.input()

        try: this_time = float(i.time)
        except: this_time = time()
        
        # web.header('Cache-Control', ('no-store, no-cache, must-revalidate,' +
        #                              'post-check=0, pre-check=0'))

        boxes = []
        boxes.append(render.box({
            "box": box('Oyster Point Marina', tag='Ha', name='Haskins', target=3.25, this_time = this_time)}))
        boxes.append(render.box({
            "box": box(current_site = 'San Francisco Bay Entrance', tag='GG', name='Golden Gate', this_time = this_time)}))
        boxes.append(render.box({
            "box": box(current_site = 'Treasure Island .5 mi N', tag='TI',
                       name='Treasure Island', this_time = this_time)}))
        boxes.append(render.box({
            "box": box('San Mateo Bridge (West)', 'San Mateo Bridge, South',
                       name='3rd Ave', tag='3rd', target=2.0, this_time = this_time)}))
        boxes.append(render.box({
            "box": box('Palo Alto', 'Dumbarton Bridge, San Francisco Bay, California Current',
                       tag='PA', name='Palo Alto', target=4.0, this_time = this_time)}))
        boxes.append(render.box({
            "box": box(current_site = 'Sherman Island (East)', tag='&Delta;',
                       name='Sherman Island', this_time = this_time)}))

        kwargs = {
            "boxes": boxes,
            "this_day": strftime("%a %h %e", localtime(this_time)),
            "time_yesterday": str(this_time - 86400),
            "date_yesterday": strftime(
                "%a %h %e", localtime(this_time - 86400)),
            "time_tomorrow": str(this_time + 86400),
            "date_tomorrow": strftime(
                "%a %h %e", localtime(this_time + 86400)),
        }
        
        return render.tides(**kwargs)

