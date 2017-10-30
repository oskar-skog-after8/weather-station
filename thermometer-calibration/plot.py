#!/usr/bin/python

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy
import math

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
    fig.set_dpi(180)
    canvas.print_png('plot.png')

if __name__ == '__main__':
    main()

