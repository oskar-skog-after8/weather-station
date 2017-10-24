#!/usr/bin/python

import os
import sys
import time

try:
    from RPi import GPIO
except ImportError:
    sys.stderr.write('Failed to import RPi.GPIO\n')
    sys.exit(1)


class template():
    def __init__(self):
        '''
        Set up the GPIO pins
        Each routine/class needs to keep track of time by itself.
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
    routines = [routine() for routine in routines]
    try:
        while True:
            i = 0
            while i < log_interval * samplerate:
                i += 1
                t = time.time()
                for routine in routines:
                    routine.collect()
                time.sleep(max(0, t + 1./samplerate - time.time()))
            # Log data
            month = time.strftime('%Y-%m', time.gmtime())
            date = time.strftime('%d', time.gmtime())
            try:
                os.mkdir(os.path.join(logdir, month))
            except OSError:
                pass
            logfile = open(os.path.join(logdir, month, date), 'a')
            for routine in routines:
                logfile.write('{} {}\n'.format(
                    time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()),
                    routine.log()
                ))
            logfile.close()
    except SystemExit:
        pass
    except KeyboardInterrupt:
        pass
    for routine in routines:
        routine.restore_GPIO()
    GPIO.cleanup()

#################

class windspeed():
    def __init__(self):
        self.MAGNETS = 3
        self.SWITCHES = [11, 7, 5, 3]
        
        self.scale = 2 * self.MAGNETS * len(self.SWITCHES)
        self.switch_status = [0 for _ in self.SWITCHES]
        self.count = 0
        for pin in self.SWITCHES:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.last_log = time.time()
    
    def collect(self):
        for index, pin in enumerate(self.SWITCHES):
            if GPIO.input(pin) != self.switch_status[index]:
                self.count += 1
                self.switch_status[index] ^= 1
    
    def log(self):
        value = float(self.count) / self.scale / (self.last_log - time.time())
        self.count = 0
        self.last_log = time.time()
        return 'Windspeed {} Hz'.format(value)
    
    def restore_GPIO(self):
        pass

class winddirection():
    def __init__(self):
            # Pin, additive value
        self.PROBE = [
            (18, 0),
            (22, 1),
            (24, 2),
            (16, 3),
        ]
        self.SCAN = [
            (8, 0),
            (10, 4),
            (12, 8),
            (26, 12),
        ]
        for pin, _ in self.SCAN:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        for pin, _ in self.PROBE:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 1)
        self.count = 0
        self.sum = 0
    
    def collect(self):
        for probe_pin, probe_value in self.PROBE:
            GPIO.output(probe_pin, 0)
            for scan_pin, scan_value in self.SCAN:
                if not GPIO.input(scan_pin):
                    self.count += 1
                    self.sum += scan_value + probe_value
            GPIO.output(probe_pin, 1)
    
    def log(self):
        if not self.count:
            return ''
        average = float(self.sum) / self.count
        self.sum = 0
        self.count = 0
        return 'Wind-direction {} Degrees'.format(22.5 * average)
    
    def restore_GPIO(self):
        pass

class temperature():
    def __init__(self):
        self.PIN = 21
        
        GPIO.setup(self.PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.count = 0
        self.switch_status = 0
        self.last_log = time.time()
    
    def collect(self):
        if GPIO.input(self.PIN) != self.switch_status:
            self.switch_status ^= 1
            self.count += 1
    
    def log(self):
        value = float(self.count) / 2 / (time.time() - self.last_log)
        self.last_log = time.time()
        self.count = 0
        return 'Temperature {} Hz'.format(value)

if __name__ == '__main__':
    main([windspeed, winddirection, temperature], 100, 60, 'log')
