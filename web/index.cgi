#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import math
import time
import os
import sys

def triangle(direction):
    return ''

def main():
    # Gather data from the log files.
    logfile = open(time.strftime(
        '/var/log/weather/%Y-%m/%d.calibrated', time.gmtime()
    ))
    timestamp = 0
    wind_speed = 0
    wind_direction = 0
    temperature = 0
    for line in logfile.read().split('\n')[-10:]:
        parts = filter(None, line.split(' '))[:4]
        if len(parts) < 4:
            continue
        if parts[0].startswith('#'):
            continue
        timestamp = calendar.timegm(time.strptime(
            ' '.join(parts[0:2]),
            '%Y-%m-%d %H:%M:%S',
        ))
        if parts[2] == 'Windspeed':
            wind_speed = int(float(parts[3])+.5)
        elif parts[2] == 'Wind-direction':
            if parts[3] == 'unknown':
                wind_direction = None
            else:
                wind_direction = parts[3]
        elif parts[2] == 'Temperature':
            temperature = int(float(parts[3])+.5)
    # Fancy graphics:
    circle_radius = 22
    svg_height = 65
    font_size = 14
    if wind_direction is not None:
        angle = math.pi*wind_direction/180
        x = 45*math.pi/180
        triangle = '<polygon points="{},{} {},{} {},{}"/>'.format(
            (svg_height/2) + math.sin(angle) * (svg_height/2),
            (svg_height/2) - math.cos(angle) * (svg_height/2),
            (svg_height/2) + math.sin(angle + x) * circle_radius,
            (svg_height/2) - math.cos(angle + x) * circle_radius,
            (svg_height/2) + math.sin(angle - x) * circle_radius,
            (svg_height/2) - math.cos(angle - x) * circle_radius,
        )
    else:
        triangle = ''
    # Language:
    if 'fi' in os.getenv('HTTP_ACCEPT_LANGUAGE', ''):
        lang = 'fi'
        title = 'Säätä'
        timeword = ' klo.'
    elif 'sv' in os.getenv('HTTP_ACCEPT_LANGUAGE', ''):
        lang = 'sv'
        title = 'Vädret'
        timeword = ' kl.'
    else:
        lang = 'en'
        title = 'Weather'
        timeword = ' at'
    # XHTML
    if 'application/xhtml+xml' in os.getenv('HTTP_ACCEPT', ''):
        mime = 'application/xhtml+xml'
    else:
        mime = 'text/html'
    sys.stdout.write('Content-Type: {}; charset=UTF-8\r\n\r\n'.format(mime))
    sys.stdout.write('''<!DOCTYPE html>
<html lang="{}" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=180, height=80"/>
        <link rel="stylesheet" href="http://aftereight.fi/ae/default.css" type="text/css"/>
        <link rel="stylesheet" href="http://aftereight.fi/ae/html/base.css" type="text/css"/>
        <link rel="stylesheet" href="/ae.css"/>
        <!--<link rel="icon" type="image/png" href=""/>-->
        <link rel="canonical" href="http://lab10.after8.fi/"/>
        <title>{}</title>
    </head>
    <body>
        <h1>{}</h1>
        <svg xmlns="http://www.w3.org/2000/svg" width="160" height="{}" style="align: center;">
            {}
            <circle cx="{}" cy="{}" r="{}"/>
            <text x="{}" y="{}">{} <tspan class="unit">m/s</tspan></text>
            <text x="90" y="35">{} <tspan class="unit">°C</tspan></text>
        </svg>
    </body>
</html>\n'''.format(
        lang,
        title,
        time.strftime('%d.%m{} %H.%M'.format(timeword), time.localtime(timestamp)),
        svg_height,
        triangle,
        (svg_height/2), (svg_height/2), circle_radius,
        (svg_height/2)-12, (svg_height/2)+(font_size/2)+1,
        wind_speed,
        '{}'.format(temperature)
    ))

if __name__ == '__main__':
    main()

