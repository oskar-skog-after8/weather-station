#!/usr/bin/python

import calendar
import cgi
import math
import os
import sys
import time

def graph():
    '''
    timespan=1h
    key=t|w
    
    avg=1
    
    width=
    height=
    round=5
    divisions=4
    
    number-size
    label-size
    '''
    form = cgi.FieldStorage()
    start_time = time.time()
    ## Read log files:
    key = {'t': 'Temperature', 'w': 'Windspeed', 'w-d': 'Wind-direction'}[form.getfirst('key')]
    timespan = form.getfirst('timespan')
    timespan_n = float(timespan.rstrip('wdhms'))
    timespan_k = timespan.lstrip('0123456789.')
    timespan = timespan_n * {'': 1, 's': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 640800}[timespan_k]
    days = int(math.ceil(timespan/86400.)) + 1
    log = []
    for i in range(-days, 1):
        try:
            file = open(time.strftime(
                '/var/log/weather/%Y-%m/%d.calibrated',
                time.gmtime(time.time() + 86400*i
            )))
        except IOError:
            continue
        lines = filter(None, file.read().split('\n'))
        for line in lines:
            line = line.lstrip()
            if line.startswith('#'):
                continue
            parts = filter(None, line.split(' '))
            if len(parts) not in (4, 5):
                continue
            if parts[2] == key:
                try:
                    value = float(parts[3])
                except:
                    value = None
                timestamp = calendar.timegm(time.strptime(
                    ' '.join(parts[:2]),
                    '%Y-%m-%d %H:%M:%S'
                ))
                if start_time - timestamp < timespan:
                    log.append((timestamp, value))
    ## Average multiple datapoints into one
    avg = int(form.getfirst('avg'))
    temp = []
    i = 0
    while i < len(log):
        sample = filter(lambda x: x[1] is not None, log[i:i+avg])
        i += avg
        n = len(sample)
        if n:
            timestamp = sum(map(lambda x: x[0], sample))/n
            if key != 'Wind-direction':
                value = sum(map(lambda x: x[1], sample))/n
            else:
                sin = sum(map(lambda x: math.sin(x[1] /180*math.pi), sample))/n
                cos = sum(map(lambda x: math.cos(x[1] /180*math.pi), sample))/n
                value = 180/math.pi* math.atan2(sin, cos)
            temp.append((timestamp, value))

    log = temp
    ## Calculate margins
    width = int(form.getfirst('width'))
    height = int(form.getfirst('height'))
    number_size = float(form.getfirst('number-size'))
    label_size = float(form.getfirst('label-size'))
    left_margin = 2*label_size + 3*number_size
    top_margin = right_margin = number_size/2
    bottom_margin = 2*label_size + number_size/2
    graph_width = width - left_margin - right_margin
    graph_height = height - top_margin - bottom_margin
    ## Heading
    sys.stdout.write('Content-Type: image/svg+xml\r\n')
    sys.stdout.write('\r\n')
    sys.stdout.write('<svg xmlns="http://www.w3.org/2000/svg" ')
    sys.stdout.write('width="{}" height="{}">\n'.format(width, height))
    sys.stdout.write('''    <style type="text/css">
        .background
        {
            fill: white;
            stroke-width: 0;
        }
        .line
        {
            stroke: black;
            stroke-width: 1px;
        }
        .number
        {
        }
        .label
        {
            text-anchor: middle;
        }
        .graph
        {
            stroke: red;
            stroke-width: 2px;
            stroke-linejoin: round;
            stroke-linecap: round;
        }
    </style>\n''')
    sys.stdout.write('<rect class="background" x="0" y="0" ')
    sys.stdout.write('width="{}" height="{}"/>\n'.format(width, height))
    ## Y divisions
    if key == 'Wind-direction':
        round = 45
        low = 0
        high = 360
        log = map(lambda x: (x[0], x[1]%360), log)
    else:
        round = int(form.getfirst('round'))
        values = map(lambda x: x[1], log)
        low = round * int(math.floor(min(values) / round))
        high = round * int(math.ceil(max(values) / round))
        if low == high:
            low -= 1
            high += 1
            round = 1
        del values
    # Avoid overlapping numbers
    spacing = graph_height / ((high-low)/round)
    modus = round * math.ceil(number_size/spacing)
    for y in range(0, high-low+1, round):
        sys.stdout.write('    <line class="line" ')
        sys.stdout.write('x1="{0}" x2="{1}" y1="{2}" y2="{2}"/>\n'.format(
            left_margin - number_size,
            width,
            height - y * graph_height/(high-low) - bottom_margin
        ))
        if not y%modus:
            sys.stdout.write('    <text class="number" ')
            sys.stdout.write('x="{}" y="{}" font-size="{}">'.format(
                2 * label_size,
                height-y*graph_height/(high-low)-bottom_margin+number_size/2,
                number_size
            ))
            sys.stdout.write('{}</text>\n'.format(y + low))
    ## X divisions
    divisions = int(form.getfirst('divisions'))
    for i in range(divisions + 1):
        sys.stdout.write('    <line class="line" ')
        sys.stdout.write('x1="{0}" x2="{0}" y1="{1}" y2="{2}"/>\n'.format(
            left_margin + (float(i)/divisions) * graph_width,
            top_margin,
            height - (0<i<divisions) * label_size*7/4
        ))
    ## Plot graph
    xlabel = form.getfirst('xlabel', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    ylabel = form.getfirst('ylabel', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    sys.stdout.write('    <text class="label" x="{0}" y="{1}" transform="rotate(90 {0} {1})" font-size="{2}">{3}</text>\n'.format(
        label_size/2,
        graph_height/2 + top_margin,
        label_size,
        ylabel
    ))
    sys.stdout.write('    <text class="label" x="{}" y="{}" font-size="{}">{}</text>\n'.format(
        graph_width/2 + left_margin,
        height - label_size/2,
        label_size,
        xlabel
    ))
    for i in range(len(log) - 1):
        x1 = (log[i][0]-start_time+timespan)/timespan
        x2 = (log[i+1][0]-start_time+timespan)/timespan
        if key == 'Wind-direction' and abs(log[i][1] - log[i+1][1]) > 180:
            if log[i][1] < 180:
                ylist = [
                    (log[i][1], log[i+1][1] - 360),
                    (log[i][1] + 360, log[i+1][1])
                ]
            else:
                ylist = [
                    (log[i][1], log[i+1][1] + 360),
                    (log[i][1] - 360, log[i+1][1])
                ]
        else:
            ylist = [(log[i][1], log[i+1][1])]
        for _y1, _y2 in ylist:
            y1 = (_y1-low) / (high-low)
            y2 = (_y2-low) / (high-low)
            sys.stdout.write('<line class="graph" ')
            sys.stdout.write('x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(
                int(0.5 + left_margin + x1*graph_width),
                int(0.5 + height - bottom_margin - y1*graph_height),
                int(0.5 + left_margin + x2*graph_width),
                int(0.5 + height - bottom_margin - y2*graph_height),
            ))
    ##
    sys.stdout.write('</svg>\n')

if __name__ == '__main__':
    if os.getenv('QUERY_STRING'):
        graph()
    else:
        if 'application/xhtml+xml' in os.getenv('HTTP_ACCEPT', ''):
            sys.stdout.write('Content-Type: application/xhtml+xml; charset=utf-8\r\n')
        else:
            sys.stdout.write('Content-Type: text/html; charset=UTF-8\r\n')
        sys.stdout.write('\r\n')
        sys.stdout.write('''<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width"/>
        <meta name="robots" content="noindex"/>
        <title>Graphs</title>
    </head>
    <body>
        <h1>Graphs</h1>
        <form action="/graph.cgi" method="GET">
            <input type="radio" name="key" value="t" checked="checked"/> Temperature<br/>
            <input type="radio" name="key" value="w"/> Windspeed<br/>
            <input type="radio" name="key" value="w-d"/> Wind direction<br/>
            <table>
                <tr>
                    <td>Timespan (number + "w", "d", "h" or "m"):</td>
                    <td><input type="text" name="timespan" value="15m"/></td>
                </tr>
                <tr>
                    <td>Sum together N points:</td>
                    <td><input type="number" name="avg" min="1" step="1" value="1"/></td>
                </tr>
                <tr>
                    <td>Round vertical divisions to:</td>
                    <td><input type="number" name="round" min="1" step="1" value="1"/></td>
                </tr>
                <tr>
                    <td>N horizontal divisions:</td>
                    <td><input type="number" name="divisions" min="1" step="1" value="1"/></td>
                </tr>
                <tr>
                    <td>Width x Height:</td>
                    <td>
                        <input type="number" name="width" value="720" min="160" step="8"/>
                        x <input type="number" name="height" value="400" min="96" step="8"/>
                    </td>
                </tr>
                <tr>
                    <td>Number font size:</td>
                    <td><input type="number" name="number-size" value="12" min="0" max="24" step="0.5"/></td>
                </tr>
                <tr>
                    <td>Label font size:</td>
                    <td><input type="number" name="label-size" value="20" min="0" max="40" step="0.5"/></td>
                </tr>
                <tr>
                    <td>X axis label:</td>
                    <td><input type="text" name="xlabel"/></td>
                </tr>
                <tr>
                    <td>Y axis label:</td>
                    <td><input type="text" name="ylabel"/></td>
                </tr>
            </table>
            <input type="submit"/>
        </form>
    </body>
</html>\n''')

