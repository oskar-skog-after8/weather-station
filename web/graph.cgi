#!/usr/bin/python

import calendar
import cgi
import time

def main():
    '''
    sum=1
    len=
    key=t|w
    days=1
    '''
    form = cgi.FieldStorage()
    days = int(form.get('days'))
    key = {'t': 'Temperature', 'w': 'Windspeed'}[form.get('key')]
    
    # Read log files:
    days += 1
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
                log.append((timestamp, value))
    #
