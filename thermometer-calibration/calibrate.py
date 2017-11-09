#!/usr/bin/python

import math
import pprint
import sys

def temperature(f, constants):
    A, B, C, D, E = [constants[key] for key in 'ABCDE']
    R = D/f - E
    T = 1/(A + B*math.log(R) + C*math.log(R)**3)
    return T-273.15

def calc_error(constants, data):
    return sum([(T-temperature(f, constants))**2 for f, T in data])

def improve(data, initial, runs, step):
    constants = initial.copy()
    n = 0
    while n < runs:
        n += 1
        for key in 'ABCD':
            original = constants[key]
            errors = []
            # Begin with 1x to keep no change at top if the errors are all equal.
            for multiplier in (1.0, 1.0 - step, 1.0 + step):
                value = original * multiplier
                constants[key] = value
                error = calc_error(constants, data)
                errors.append((value, error))
            errors.sort(key=lambda x: x[1])
            constants[key] = errors[0][0]
            sys.stderr.write('Run {}: {}={:.10f}, \terror: {:.10f}\n'.format(
                n, key, value, errors[0][1]
            ))
    return constants 

def main():
    data = [(float(f), float(T)) for f, T, _ in eval(open('data.py').read())]
    constants = {
        #1/T = A + B*ln(R) + C*ln(R)^3      # Steinhart-Hart
        #R = (1/f)D - E
        #D = 1/(2*ln(2)*C1) # C1 is the capacitor
        #E = R2/2           # R2 is the other resistor (between discharge and VDD)
        'A': 6.997 *10**-4, # Beta to Steinhart-Hart
        'B': 2.882 *10**-4, # Beta to Steinhart-Hart
        'C': 1.0 *10**-7,   # Experimented
        'D': 1.5 *10**5,    # 4.7 uF
        'E': 1.07 *10**3,   # 2.14 kOhm MEASURED
    }
    constants = improve(data, constants, 1000, 0.01)
    f = open('calibration.out', 'w')
    f.write(pprint.pformat(constants))
    f.close()

if __name__ == '__main__':
    main()

