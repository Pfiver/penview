#!/usr/apps/Python/bin/python

import matplotlib, sys
matplotlib.use('TkAgg')

from numpy import arange, sin, pi
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from Tkinter import *

master = Tk()
master.title("Hello World!")
#-------------------------------------------------------------------------------

f = Figure(figsize=(5,4), dpi=100)
a = f.add_subplot(111)
t = arange(0.0,3.0,0.01)
s = sin(2*pi*t)

a.plot(t,s)

dataPlot = FigureCanvasTkAgg(f, master=master)
dataPlot.show()
#dataPlot.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

toolbar = Frame(master)
button = Button(toolbar, text="Push me")
button.pack()
toolbar.pack()


#toolbar.grid(row=1, column=1, sticky="ew")
dataPlot.get_tk_widget().grid(row=1, column=1, sticky="nsew")
#master.grid_rowconfigure(0, weight=0)
#master.grid_rowconfigure(1, weight=1)
#master.grid_columnconfigure(0, weight=1)

#-------------------------------------------------------------------------------
master.mainloop()

