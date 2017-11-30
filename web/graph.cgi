#!/usr/bin/python

import calendar
import cgi
import math
import sys
import time

def main():
    '''
    timespan=1h
    key=t|w
    days=1
    
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
    days = int(form.getfirst('days'))
    days += 1
    key = {'t': 'Temperature', 'w': 'Windspeed'}[form.getfirst('key')]
    timespan = form.getfirst('timespan')
    timespan_n = float(timespan.rstrip('wdhms'))
    timespan_k = timespan.lstrip('0123456789.')
    timespan = timespan_n * {'': 1, 's': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 640800}[timespan_k]
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
                if parts[3] != 'unknown':
                    value = float(parts[3])
                else:
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
        a = sum(map(lambda x: x[0], sample))
        b = sum(map(lambda x: x[1], sample))
        n = len(sample)
        if n:
            temp.append((a/n, b/n))
    log = temp
    ## Calculate margins
    width = int(form.getfirst('width'))
    height = int(form.getfirst('height'))
    number_size = float(form.getfirst('number-size'))
    label_size = float(form.getfirst('label-size'))
    left_margin = label_size + 3*number_size + 1
    top_margin = right_margin = number_size/2
    bottom_margin = label_size + 1 + number_size/2
    graph_width = width - left_margin - right_margin
    graph_height = height - top_margin - bottom_margin
    ## Heading
    sys.stdout.write('Content-Type: image/svg\r\n')
    sys.stdout.write('\r\n')
    sys.stdout.write('<svg xmlns="http://www.w3.org/2000/svg" ')
    sys.stdout.write('width="{}" height="{}">\n'.format(width, height))
    sys.stdout.write('''    <style type="text/css">
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
        }
        .graph
        {
            stroke: red;
            stroke-width: 2px;
            stroke-linejoin: round;
            stroke-linecap: round;
        }
    </style>\n''')
    ## Y divisions
    round = int(form.getfirst('round'))
    values = map(lambda x: x[1], log)
    low = int(round * math.floor(min(values) / round))
    high = int(round * math.ceil(max(values) / round))
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
                label_size + 1,
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
            height
        ))
    ## Plot graph
    for i in range(len(log) - 1):
        x1 = (log[i][0]-start_time+timespan)/timespan
        x2 = (log[i+1][0]-start_time+timespan)/timespan
        y1 = (log[i][1]-low) / (high-low)
        y2 = (log[i+1][1]-low) / (high-low)
        sys.stdout.write('    <line class="graph" ')
        sys.stdout.write('x1="{}" y1="{}" x2="{}" y2="{}"/>\n'.format(
            left_margin + x1*graph_width,
            height - bottom_margin - y1*graph_height,
            left_margin + x2*graph_width,
            height - bottom_margin - y2*graph_height,
        ))
    ##
    sys.stdout.write('</svg>\n')


if __name__ == '__main__':
    main()

