#!/usr/bin/python

import math

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
    '''Transform the newly read line.'''
    pass

def main():
    pass


if __name__ == '__main__':
    main()


