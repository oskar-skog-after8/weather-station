#!/usr/bin/python

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy
import math

def beta(cold=-50., hot=100., frequency_step=.1):
    a = 3470.
    b = 1100.
    c = 139.574
    d = 2.4281
    
    f_list = []
    T_list = []
    f = 0.0
    while True:
        f += frequency_step
        T = a/(math.log(-b*(f-c)/f) + d) - 273.15
        if T < cold:
            continue
        if T > hot:
            break
        f_list.append(f)
        T_list.append(T)
    
    return f_list, T_list
    

def main():
    fig = Figure()
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(111)
    data = eval(open('data.py').read())
    colors = {
        'terrible': '#ff5555',
        'bad': '#aa0000',
        'moderate': '#ff00ff',
        'good': '#5555ff',
    }
    for f, T, key in data:
        ax.plot(float(f), float(T), marker='.', color=colors[key])
    ax.plot(*beta())
    fig.set_dpi(180)
    canvas.print_png('plot.png')

if __name__ == '__main__':
    main()

