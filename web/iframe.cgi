#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import math
import time
import os
import sys

def main():
    # Gather data from the log files.
    try:
        logfile = open(time.strftime(
            '/var/log/weather/%Y-%m/%d.calibrated', time.gmtime()
        ))
    except IOError:
        logfile = open(time.strftime(
            '/var/log/weather/%Y-%m/%d.calibrated', time.gmtime(time.time() - 86400)
        ))
    timestamp = 0
    wind_speed = 0
    wind_direction = 0
    #temperature = ''
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
                wind_direction = float(parts[3])
        elif parts[2] == 'Temperature':
            try:
                temperature = float(parts[3])
                if temperature < 0:
                    temperature = int(temperature-.5)
                else:
                    temperature = int(temperature+.5)
                temperature = str(temperature)
            except ValueError:
                temperature = '?'
    # Fancy graphics:
    if wind_speed < 10:
        wind_speed = '&#160;{}&#160;'.format(wind_speed)
    circle_radius = 22
    svg_height = 66
    font_size = 25
    indent = 10
    if wind_direction is not None:
        angle = math.pi*wind_direction/180
        x = 45*math.pi/180
        triangle = '<polygon points="{},{} {},{} {},{}"/>'.format(
            indent+(svg_height/2) + math.sin(angle) * (svg_height/2),
            (svg_height/2) - math.cos(angle) * (svg_height/2),
            indent+(svg_height/2) + math.sin(angle + x) * circle_radius,
            (svg_height/2) - math.cos(angle + x) * circle_radius,
            indent+(svg_height/2) + math.sin(angle - x) * circle_radius,
            (svg_height/2) - math.cos(angle - x) * circle_radius,
        )
    else:
        triangle = ''
    stylesheet ='''
#wind
{
    fill: #ccddcc;
    font-size: 25px;
}
#wind polygon
{
    fill: #b5c4b5;
}
#temperature
{
    font-size: 40px;
}
text
{
    font-family: impact;
    fill: #e6298b;
    font-weight: normal;
}
.unit
{
    font-family: verdana;
    fill: #000000;
    font-size: 10pt;
    font-weight: normal;
}
#wind .unit
{
    baseline-shift: sub;
}

body
{
    width: 180px;
}
p
{
    text-align: center;
    margin-top: -10px;
    font-family: verdana;
}
'''
    # Language:
    if 'fi' in os.getenv('HTTP_ACCEPT_LANGUAGE', ''):
        lang = 'fi'
        title = 'Säätä'
        timestr = '%d.%m.%Y klo. %H.%M'
    elif 'sv' in os.getenv('HTTP_ACCEPT_LANGUAGE', ''):
        lang = 'sv'
        title = 'Vädret'
        timestr = '%d.%m.%Y kl. %H.%M'
    else:
        lang = 'en'
        title = 'Weather'
        timestr = '%Y-%m-%d at %H:%M'
    # XHTML
    if 'application/xhtml+xml' in os.getenv('HTTP_ACCEPT', ''):
        mime = 'application/xhtml+xml'
    else:
        mime = 'text/html'
    # Output
    sys.stdout.write('Content-Type: {}; charset=UTF-8\r\n'.format(mime))
    sys.stdout.write('Refresh: 15\r\n')
    sys.stdout.write('\r\n')
    sys.stdout.write('''<!DOCTYPE html>
<html lang="{}" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=180, height=74"/>
        <link rel="stylesheet" href="http://aftereight.fi/ae/default.css" type="text/css"/>
        <link rel="stylesheet" href="http://aftereight.fi/ae/html/base.css" type="text/css"/>
        <link rel="stylesheet" href="http://aftereight.fi/ae/html/default.css" type="text/css"/>
        <style type="text/css">{}</style>
        <!--<link rel="icon" type="image/png" href=""/>-->
        <link rel="canonical" href="http://lab10.after8.fi/"/>
        <title>{}</title>
    </head>
    <body>
        <svg xmlns="http://www.w3.org/2000/svg" width="180" height="{}" style="align: center;">
            <g id="wind">
                {}
                <circle cx="{}" cy="{}" r="{}"/>
                <text x="{}" y="{}">{} <tspan class="unit">&#160;m/s</tspan></text>
            </g>
            <g id="temperature">
                <text x="{}" y="{}">{} <tspan class="unit">°C</tspan></text>
            </g>
        </svg>
        <!--<p>{}</p>-->
    </body>
</html>\n'''.format(
        lang,
        stylesheet,
        title,
        svg_height,
        triangle,
        (svg_height/2)+indent, (svg_height/2), circle_radius,
        (svg_height/2)+indent-13, (svg_height/2)+(font_size/2)-4, wind_speed,
        100, (svg_height/2)+(circle_radius*2/3), temperature,
        time.strftime(timestr, time.localtime(timestamp)),
    ))

if __name__ == '__main__':
    main()

