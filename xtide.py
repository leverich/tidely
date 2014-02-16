#!/usr/bin/env python

import os
import re
#from gevent.subprocess import Popen, PIPE
from subprocess import Popen, PIPE
import sys
import time

curdir = os.path.dirname(__file__)
default_tcd = curdir + "/tcd/harmonics-2004-rebuild.tcd"

def run_xtide(site_name, start_time = None, stop_time = None, tcd_file = default_tcd):
    """Run XTide's command-line tool to compute tide magnitudes for each
    minute between start_time and stop_time.

    Arguments:
        site_name: XTide station name. May be an elevation or current station.
        start_time: Unix-time (seconds). Defaults to now.
        stop_time: Unix-time (seconds). Defaults to now + 12 hours.
        tcd_file: Path of XTide "TCD" tidal constituents database file to use.
    Returns: [[unix-time, magnitude], ...]
    Throws: ValueError, CalledProgramError, Exception

    """
    try:    start_time = float(start_time)
    except: start_time = time.time()
    try:    stop_time  = float(stop_time)
    except: stop_time  = start_time + 12*60*60

    # Munge site_name. We pass this as an argument to xtide, and we
    # don't know what kind of validation they do on its command-line
    # arguments.
    site_name_clean = re.sub('[^A-Za-z0-9()., ]', '', site_name[0:100])
    if site_name != site_name_clean: raise Exception("INVALID_SITE")

    start_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(start_time))
    stop_str  = time.strftime("%Y-%m-%d %H:%M", time.localtime(stop_time))

    # tcd_file gets passed to XTide as an environment variable.
    _env = dict(os.environ)
    if tcd_file: _env["HFILE_PATH"] = tcd_file

    (xtide, xtide_err) = Popen(
        ["tide", "-l", site_name,
         "-b", start_str, "-e", stop_str,
         "-m", "r", "-s", "00:01"],
        stdout=PIPE, stderr=PIPE,
        env=_env).communicate()

    # Check for XTide errors.
    m = re.search('XTide (?:Fatal )?Error:\s+.*$', xtide_err, re.MULTILINE)
    if m: raise Exception(m.group(0))

    # Otherwise, parse tide predictions.
    p = re.compile('^([\d.]+)\s+([-\d.]+)$', re.M)

    return [ [int(seconds), float(level)]
             for (seconds, level) in re.findall(p, xtide) ]

def target_spans(levels, target = 0.0, levels2 = None, target2 = 0.0,
                 maxima = False, now = False):
    """Convert list of tide predictions (from run_xtide(site)) into
    spans. A new span is created each time a sequence of tide
    predictions crosses a target magnitude (default 0.0). If levels2
    and target2 are given, a new span is created if either set of
    predictions crosses its target.

    If two lists are given, their times must align exactly or the
    output is undefined.

    A span is of the form:
       { state: int, start: float, end: float,
         maximum: [ magnitude, time ],
         now: [ magnitude, time ] }

    Start and end are unix timestamps. State encodes which of level
    and level2 is above its target:

        3 if level2 and level is above target
        2 if level2 is above target
        1 if level is above target
        0 if neither is above target

    maximum and now are optional, and mark events within a span.

    """
    assert len(levels) > 1

    try: target = float(target)
    except: target = 0.0
    try: target2 = float(target2)
    except: target2 = 0.0

    # Basic sanity check when given two lists of predictions.
    if levels2:
        assert(len(levels) == len(levels2))
        assert(levels[0][0] == levels2[0][0])

    # Initialization.
    last_state = None
    last_time = levels[0][0]
    this_time = levels[0][0]

    now_buffer = None
    if now:
        now_time = time.time()
        lt_now = levels[0][0] < now_time

    max_buffer = None
    if maxima:
        prev_level = None
        prev_dir = None
        prev_time = None

    if levels2:
        zip_levels = zip(levels, levels2)
    else:
        zip_levels = zip(levels, [[None, None] for i in range(len(levels))])

    # Helper functions.
    def get_state(a, b = None):
        return ((0 if              a < target  else 1) +
                (0 if b is None or b < target2 else 2))

    def make_span(last_state, last_time, this_time,
                  now_buffer, max_buffer):
        span = { "state": last_state,
                 "start": last_time,
                 "end":   this_time - 1 }
        if now_buffer: span['now'] = now_buffer
        if max_buffer: span['maximum'] = max_buffer
        return span

    # The meat.
    spans = []
    for ((seconds, level), (seconds2, level2)) in zip_levels:
        this_state = get_state(level, level2)
        this_time = seconds

        if now and lt_now and this_time > now_time:
            now_buffer = [ level, seconds ]
            lt_now = False

        # Scan levels for a point of inflection.
        if maxima:
            if prev_level:
                this_dir = prev_level < level
                if prev_dir is not None and this_dir != prev_dir:
                    max_buffer = [ prev_level, prev_time ]
                prev_dir = this_dir
            prev_level = level
            prev_time = this_time

        # Create a new span at any boundary where a level crosses its target.
        if last_state is not None and this_state != last_state:
            spans.append(make_span(last_state, last_time, this_time,
                                   now_buffer, max_buffer))
            now_buffer = None
            max_buffer = None
            last_time = this_time

        last_state = this_state

    spans.append(make_span(last_state, last_time, this_time,
                           now_buffer, max_buffer))
    return spans

def xtide_graph(site_name, start_time = None, tcd_file = None):
    site_name_clean = re.sub('[^A-Za-z0-9()., ]', '', site_name[0:100])
    if site_name != site_name_clean: raise Exception("INVALID_SITE")
    if start_time is None: start_time = time.time()

    # Clamp start_time to beginning and end of day.
    start_str = time.strftime("%Y-%m-%d 00:00", time.localtime(start_time))
    stop_str = time.strftime("%Y-%m-%d 23:59", time.localtime(start_time))

    # tcd_file gets passed to XTide as an environment variable.
    _env = dict(os.environ)
    if tcd_file: _env["HFILE_PATH"] = tcd_file

    (xtide, xtide_err) = Popen(
        ["tide", "-l", site_name,
         "-b", start_str, "-e", stop_str,
         "-m", "g", "-f", "p",
         "-hf", "%H", "-gw", "550",
         "-nc", "Gray", "-dc", "White",
         "-ga", "1.155", "-nf", "y",
         "-fc", "Red", "-ec", "DarkBlue",
         "-df", "%a, %m/%d/%y", ],
        stdout=PIPE, stderr=PIPE,
        env=_env).communicate()

    return str(xtide)
