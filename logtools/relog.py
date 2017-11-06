#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import math
import time

def temperature(f, calibration):
    '''
    Returns temperature in degrees celcius.
    Input is the measured frequency from the 555.
    
    1/T = A + B*ln(R) + C*ln(R)^3
    R = (1/f)D - E
    
    D = 1/(2*ln(2)*C1)  # C1 is the capacitor
    E = R2/2            # R2 is the other resistor (between discharge and VDD)
    '''
    A, B, C, D, E = [calibration[key] for key in 'ABCDE']
    R = D/f - E
    T = 1/(A + B*math.log(R) + C*math.log(R)**3)
    return T-273.15

def windspeed(x, calibration):
    return x*calibration['k']

def winddirection(a, calibration):
    return a+calibration['north']


def parseline(line):
    '''Transform the newly read line.
    Accepts a string without line breaks and emits a string without linebreaks.
    
    <date> <time> <key> <value> <unit>
    '''
    mapping = {
        'Windspeed': (windspeed, 'm/s'),
        'Wind-direction': (winddirection, '°'),
        'Temperature': (temperature, '°C'),
    }
    
    parts = filter(None, line.split(' '))
    if len(parts) in (3, 5):
        timestamp = '{} {}'.format(parts[0], parts[1])
        parts = parts[2:]
    if len(parts) == 3:
        key, value, _ = parts
        function = mapping[key][0]
        calibration = eval(open('/usr/local/lib/weather/calibration').read())[key]
        try:
            new_value = function(float(value), calibration)
        except:
            new_value = '<error>'
        new_unit = mapping[key][1]
        return '{} {} {} {}'.format(timestamp, key, new_value, new_unit)
    elif len(parts) == 1:
        return '{} {} Unknown/error'.format(timestamp, key)
    else:
        return '{} ERROR: {}'.format(
            time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
            line
        )

def main():
    logdir = '/var/log/weather'
    # Past
    t = time.time()     # Avoid exceptionally rare race conditions.
    for n in range(1, 7):
        name = os.path.join( \
            logdir, time.strftime('%Y-%m/%d', time.gmtime(t-n*86400)))
        input = open(name)
        output = open(name + '.calibrated', 'w')
        for line in filter(None, input.read().split('\n')):
            output.write(parseline(line) + '\n')
        output.close()
        input.close()
    # Now
    while True:
        t = time.time()
        today = os.path.join( \
            logdir, time.strftime('%Y-%m/%d', time.gmtime(t)))
        tomorrow = os.path.join( \
            logdir, time.strftime('%Y-%m/%d', time.gmtime(t+86400)))
        # Don't append
        output = open(os.path.join(today + '.calibrated'), 'w')
        index = 0
        # Cycle files tomorrow.
        while not os.path.exists(tomorrow):
            # Seek to previous EOF.
            size = os.stat(today).st_size
            if size > index:
                input = open(today)
                input.seek(index)
                # Outsource the actual processing.
                for line in filter(None, input.read().split('\n')):
                    output.write(parseline(line) + '\n')
                output.flush()
                index = size
                input.close()
            time.sleep(10)
        output.close()

if __name__ == '__main__':
    main()

