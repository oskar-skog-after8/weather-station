#!/usr/bin/python

import math

def temperature(f):
    '''
    Returns temperature in degrees celcius.
    Input is the measured frequency from the 555.
    
    1/T = A + B*ln(R) + C*ln(R)^3
    R = (1/f)D - E
    
    D = 1/(2*ln(2)*C1)  # C1 is the capacitor
    E = R2/2            # R2 is the other resistor (between discharge and VDD)
    '''
    A = 6.997 *10**-4   # Beta to Steinhart-Hart
    B = 2.882 *10**-4   # Beta to Steinhart-Hart
    C = 0               # Beta to Steinhart-Hart
    D = 1.5 *10**5      # 4.7 uF
    E = 1.1 *10**3      # 2.2 kOhm
    
    R = D/f - E
    T = 1/(A + B*math.log(R) + C*math.log(R)**3)
    return T-273.15
