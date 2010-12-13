from random import *
from Tkinter import *

# The "view"
class PenViewUI:
    def __init__(self):

        # tk object
        self.tk = Tk() # the main window

        # level 0 widget
        self.frame0 = Frame(self.tk) # top-level container widget

        # level 1 widgets
        self.plot_region = ScrollRegion(self.frame0)
        self.button_region = Frame(self.frame0, height=50) # button container

        # level 2 widget
        self.xy_plot = XYPlot(self.plot_region, 800, 600) # custom canvas widget
        # level 2 widgets
        Quit = Button(self.button_region, text="Quit", command=self.frame0.quit)
        PlotData = Button(self.button_region, text="Draw Data", command=self.xy_plot.plot_random_data)
        Rectangle = Button(self.button_region, text="Draw Rectangle", command=self.xy_plot.draw_rectangle)

        # bind our map handler
        self.xy_plot.bind("<Map>", self.map_handler)

        # pack level 0 widget
        self.frame0.pack()

        # pack level 1 widgets
#        self.button_region.pack_propagate(0)
#        self.button_region.pack(fill=None, expand=0)
        self.button_region.pack(fill=BOTH, side=BOTTOM)
        for frm in self.plot_region,:
            frm.pack(fill=BOTH, expand=1)

        # pack level 2 widget
        self.xy_plot.pack()
        # pack level 2 widgets
        for btn in Quit, Rectangle, PlotData:
#            btn.pack_propagate(0)
            btn.pack(side=RIGHT)

    def tk_mainloop(self):
        self.tk.mainloop()

    def map_handler(self, event):
        # Here we'd have to check the original height of the
        # top-level frame and subtract the height of the xy_plot
        # to find out how much space the buttons take u, height=50p
        # - but we use scrollbars now anyway and don't resize the xy_plot canvas on window resize
        pass
#        print event.widget.__class__
#        print "w: %d" % self.frame0.winfo_width()
#        print "W: %d" % self.xy_plot.winfo_width()
#        print "h: %d" % self.frame0.winfo_height()
#        print "H: %d" % self.xy_plot.winfo_height()

class ScrollRegion(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.xscrollbar = Scrollbar(self, orient=HORIZONTAL)
        self.yscrollbar = Scrollbar(self, orient=VERTICAL)
        self.xscrollbar.grid(row=1, column=0, sticky=E+W)
        self.yscrollbar.grid(row=0, column=1, sticky=N+S)

    def child_added(self, child_widget):
        self.xscrollbar.config(command=child_widget.xview)
        self.yscrollbar.config(command=child_widget.yview)
        child_widget.grid(row=0, column=0, sticky=N+S+E+W)
        child_widget.configure(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set,
                               scrollregion=(0, 0, child_widget.winfo_width(), child_widget.winfo_height()))

# a custom canvas to display xy-plots
class XYPlot(Canvas):
    """
    """
    def __init__(self, _parent, _width, _height):
        self.parent = _parent
        self.width, self.height = _width, _height

        self.fgcolor = "black"
        self.bgcolor = "#EEEEEE"
        Canvas.__init__(self, self.parent, bg=self.bgcolor,
                              width=self.width, height=self.height)

        self.draw_axes(self.fgcolor)
        self.bind('<Configure>', self.resize_handler)

    def pack(self):
#        Canvas.pack(self)
        if self.parent.__class__ == ScrollRegion:
            self.parent.child_added(self)

    def draw_axes(self, _color="black"):
        self.create_rectangle(0, 0, self.width, self.height, fill=self.bgcolor)
        self.create_line(0, self.height / 2, self.width, self.height / 2, width=2, fill=_color)
        self.create_line(self.width / 2, 0, self.width / 2, self.height, width=2, fill=_color)

    def draw_rectangle(self):
        self.draw_axes()
        self.create_rectangle(self.width / 2 - self.width / 10,
                              self.height / 2 - self.height / 10,
                              self.width / 2 + self.width / 10,
                              self.height / 2 + self.height / 10, fill="blue")

    def plot_random_data(self):
        self.draw_axes()
        data = []
        for i in range(0, self.width, self.width / 50):
            data.append(i)
            data.append(self.height - (randint(0, self.height)))
        self.create_line(data, fill=self.drawcolor)

    def resize_handler(self, event):
        pass
#        print "w: %d" % self.winfo_width()
#        print "W: %d" % self.parent.winfo_width()
#        print "h: %d" % self.winfo_height()
#        print "H: %d" % self.parent.winfo_height()
#        self.repaint(self.bgcolor)
#        self.width = event.width
#        self.height = event.height
#        self.canvas.configure(width=self.width, height=self.height)
#        self.repaint(self.fgcolor)
