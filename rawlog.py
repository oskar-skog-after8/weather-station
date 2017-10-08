#!/usr/bin/python

import os
import sys
import time

try:
    import GPIO from RPi
except ImportError:
    sys.stderr.write('Failed to import RPi.GPIO\n')
    sys.exit(1)


class template():
    def __init__(self, samplerate, log_interval):
        '''
        Set up the GPIO pins
        Configure the `collect` method for the `samplerate` and `log_interval`
        '''
        pass
    def collect(self):
        '''
        Collect data.
        '''
        pass
    def log(self):
        '''
        Return a formatted string without line breaks.
        '''
        pass
    def restore_GPIO(self):
        '''
        Clean up the GPIO pins.
        '''
        pass

def main(routines, samplerate, log_interval, logdir):
    GPIO.setmode(GPIO.BOARD)
    routines = [routine(samplerate) for routine in routines]
    try:
        while True:
            i = 0
            while i < log_interval * samplerate
                i += 1
                t = time.time()
                for routine in routines:
                    routine.collect()
                time.sleep(t + 1./samplerate - time.time())
            for routine in routines:
                # TODO
                print(routine.log(logdir))
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    for routine in routines:
        routine.restore_GPIO()
    GPIO.cleanup()

#################

class windspeed():
    def __init__(self, samplerate, log_interval):
        self.MAGNETS = 3
        self.SWITCHES = [11, 7, 5, 3]
        
        self.samplerate = samplerate
        self.log_interval = log_interval
        
        self.switch_status = [0 for _ in self.SWITCHES]
        self.count = 0
        for pin in self.SWITCHES:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    def collect(self):
        for index, pin in enumerate(self.SWITCHES):
            if GPIO.input(pin) != self.switch_status[index]:
                self.count += 1
                self.switch_status[index] ^= 1
    
    def log(self):
        value = float(self.count) / (self.MAGNETS*len(self.SWITCHES)) / 2.0
        value /= (self.samplerate * self.log_interval)
        self.count = 0
        return '{} Hz'.format(value)
    
    def restore_GPIO(self):
        pass



if __name__ == '__main__':
    main([windspeed, winddirection, temperature], 100, 60, '.')
