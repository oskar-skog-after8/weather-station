#!/usr/bin/python

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy
import math

def approx(cold=-50., hot=100., frequency_step=.05):
    constants = {'A': 0.0007251313349840727,
     'B': 0.00017970001880764384,
      'C': 1.1574958957074605e-06,
       'D': 182297.81778392274,
        'E': 1100.0}
        
  
    A, B, C, D, E = [constants[key] for key in 'ABCDE']
    
    f_list = []
    T_list = []
    f = 0.0
    while True:
        f += frequency_step
        R = D/f - E
        T = 1.0/(A + B*math.log(R) + C*math.log(R)**3)
        T -= 273.15
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
    ax.plot(*approx())
    fig.set_dpi(270)
    canvas.print_png('plot.png')

if __name__ == '__main__':
    main()

