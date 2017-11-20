#!/usr/bin/python
# -*- coding: utf-8 -*-

import calendar
import time
import os
import sys

def svg(speed, direction):
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
            wind_speed = float(parts[3])
        elif parts[2] == 'Wind-direction':
            if parts[3] == 'unknown':
                wind_direction = None
            else:
                wind_direction = parts[3]
        elif parts[2] == 'Temperature':
            temperature = int(float(parts[3])+.5)
    # Language:
    if 'fi' in os.getenv('HTTP_ACCEPT_LANGUAGE', ''):
        lang = 'fi'
        title = 'Säätä'
        timeword1 = ' klo.'
        timeword2 = ''
    elif 'sv' in os.getenv('HTTP_ACCEPT_LANGUAGE', ''):
        lang = 'sv'
        title = 'Vädret'
        timeword1 = ' kl.'
        timeword2 = ''
    else:
        lang = 'en'
        title = 'Weather'
        timeword1 = ' at'
        timeword2 = " o'clock"
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
        <link rel="stylesheet" href="http://aftereight.fi/ae/html/base.css" type="text/css"/>
        <link rel="stylesheet" href="/weather.css" type="text/css"/>
        <!--<link rel="icon" type="image/png" href=""/>-->
        <link rel="canonical" href="http://lab10.after8.fi/"/>
        <title>{}</title>
    </head>
    <body>
        <h1>{}</h1>
        <div>
            <div id="wind">
                {}
            </div>
            <div id="temperature">
                <p>{}</p>
            </div>
        </div>
    </body>
</html>\n'''.format(
        lang,
        title,
        time.strftime('%d.%m{} %H.%M{}'.format(timeword1, timeword2), time.localtime(timestamp)),
        svg(wind_speed, wind_direction),
        '{} °C'.format(temperature)
    ))

if __name__ == '__main__':
    main()

