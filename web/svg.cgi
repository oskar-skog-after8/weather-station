#!/usr/bin/python

import os
import sys
import time

def pagination(key):
    key_format = '%Y%m%d%H'     # NOTE: Will convert to int for comparisons
    low_cap = '2017120721'
    data = {
        'hourly': {
            'delta': 3600,
            'format': 'hourly/%Y-%m/%d/%H',
        },
        'daily': {
            'delta': 86400,
            'format': 'daily/%Y-%m/%d',
        },
        'weekly': {
            'delta': 604800,
            'format': 'weekly/%Y-%V',
        },
    }
    
    high_cap = time.strftime(key_format, time.localtime(t - 3600))
    if not key:
        key = high_cap
    t = time.mktime(time.strptime(key_format, key))
    values = {}
    for key in data:
        prev = time.strftime(key_format, time.localtime(t - data[key]['delta']))
        next = time.strftime(key_format, time.localtime(t + data[key]['delta']))
        if int(prev) < int(low_cap):
            prev = low_cap
        if int(next) >= int(high_cap):
            next = ''   # Default
        values[key] = {
            'prev': prev,
            'next': next,
            'file': time.strftime(data[key]['format'], time.localtime(t)),
        }
    return values


def main():
    pass


if __name__ == '__main__':
    main()


