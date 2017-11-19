#!/bin/sh

echo 'Content-Type: text/plain; charset=UTF-8'
echo

tail -n 3 /var/log/weather/$(date '+%Y-%m/%d').calibrated
