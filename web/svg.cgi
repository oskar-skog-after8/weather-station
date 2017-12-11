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
    
    high_cap = time.strftime(key_format, time.localtime(time.time() - 3600))
    if not key:
        key = high_cap
    t = time.mktime(time.strptime(key, key_format))
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
    key = os.getenv('QUERY_STRING')
    
    if 'application/xhtml+xml' in os.getenv('HTTP_ACCEPT', ''):
        sys.stdout.write('Content-Type: application/xhtml+xml; charset=UTF-8\r\n')
    else:
        sys.stdout.write('Content-Type: text/html; charset=UTF-8\r\n')
    if not key:
        sys.stdout.write('Refresh: 15\r\n')
    sys.stdout.write('\r\n')
    
    sys.stdout.write('''<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en">
    <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width"/>
        <!--<meta name="robots" content="noindex, nofollow"/>-->
        <link rel="icon" href="/favicon.png"/>
        <title>Weather graphs</title>
    </head>
    <body>
        <h1>Weather graphs</h1>\n''')
    
    pagination_data = pagination(key)
    timeframe_order = ['weekly', 'daily', 'hourly']
    timeframe_data = {
        'hourly': {
            'h2': 'Hourly',
            'prev': 'Previous hour',
            'next': 'Next hour',
        },
        'daily': {
            'h2': 'Daily',
            'prev': 'Previous day',
            'next': 'Next day',
        },
        'weekly': {
            'h2': 'Weekly',
            'prev': 'Previous week',
            'next': 'Next week',
        }
    }
    parameter_list = [
        {
            'name': 'temperature',
            'h3': 'Temperature',
            'remark': '',
        },
        {
            'name': 'windspeed',
            'h3': 'Wind speed',
            'remark': '',
        },
        {
            'name': 'wind-direction',
            'h3': 'Wind heading',
            'remark': '0 = North, 90 = East, 180 = South, 270 = West.  Direction to which the wind blows.'
        },
    ]
    for time_key in timeframe_order:
        sys.stdout.write('        <div class="time">\n')
        sys.stdout.write('            <h2>{}</h2>\n'.format(timeframe_data[time_key]['h2']))
        for parameter in parameter_list:
            sys.stdout.write('            <div class="parameter">\n')
            sys.stdout.write('                <h3>{}</h3>\n'.format(parameter['h3']))
            image = '/svg/{}.{}.svg'.format(pagination_data[time_key]['file'], parameter['name'])
            sys.stdout.write('                <img src="{}"/>\n'.format(image))
            if parameter['remark']:
                sys.stdout.write('                <p class="remark">{}</p>\n'.format(parameter['remark']))
            sys.stdout.write('            </div>\n')
        sys.stdout.write('            <p class="links">\n')
        for direction in ('prev', 'next'):
            sys.stdout.write('                <a class="{}" href="/svg.cgi?{}">{}</a>\n'.format(
                direction,
                pagination_data[time_key][direction],
                timeframe_data[time_key][direction]
            ))
        sys.stdout.write('            </p>\n')
        sys.stdout.write('        </div>\n')
    
    sys.stdout.write('    </body>\n</html>\n')


if __name__ == '__main__':
    main()


