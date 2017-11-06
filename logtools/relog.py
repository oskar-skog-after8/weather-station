#!/usr/bin/python

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
    '''
    pass

def main():
    while True:
        t = time.time()     # Avoid exceptionally rare race conditions.
        today = os.path.join(logdir,
            time.strftime('%Y-%m/%d', time.gmtime(t)))
        tomorrow = os.path.join(logdir,
            time.strftime('%Y-%m/%d', time.gmtime(t+86400)))
        output = open(os.path.join(today + '.calibrated'), 'a')
        index = 0
        # Cycle files tomorrow.
        while not os.path.exists(tomorrow)):
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

