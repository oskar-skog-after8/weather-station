#!/usr/bin/python

import calendar
import cgi
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
    '''
    form = cgi.FieldStorage()
    # Read log files:
    days = int(form.get('days'))
    days += 1
    key = {'t': 'Temperature', 'w': 'Windspeed'}[form.get('key')]
    timespan = form.get('timespan')
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
                if time.time() - timestamp < timespan:
                    log.append((timestamp, value))
    # Average multiple datapoints into one
    avg = int(form.get('avg'))
    log2 = []
    i = 0
    while i < len(log):
        sample = filter(lambda x: x[1] is not None, log[i:i+avg])
        i + = avg
        a = sum(map(lambda x: x[0], sample))
        b = sum(map(lambda x: x[1], sample))
        n = len(sample)
        if n:
            log2.append((a/n, b/n))
    # 
