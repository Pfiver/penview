from Tkinter import *
from functools import partial

class DataRegion(Frame):
    def __init__(self, parent, pvconf):
        Frame.__init__(self, parent)
        
        self.plot_region = ScrollRegion(self)
        self.xy_plot = XYPlot(self.plot_region, 800, 600) # custom canvas widget
        
        self.controls_region = Frame(self)

        # controls_region setup - keep pack()ing order !
        # y-axis controls 
        self.vars = []
        self.y_scales = []
        self.y_units = []
        for i in range(2):
            v = StringVar()
            self.vars.append(v)
            v.trace("w", partial(self.controls_handler, v))
            sb = Spinbox(self.controls_region, from_=0, to=99, width=5, textvariable=v)
            sb.pack(side=LEFT)
            self.y_scales.append(sb)

            ul = Label(self.controls_region, text="y%d units" % i)
            ul.pack(side=LEFT)
            self.y_units.append(ul)

        # x-axis controls
        self.x_units = Label(self.controls_region, text="x units")
        self.x_units.pack(side=RIGHT)

        v = StringVar()
        self.vars.append(v)
        v.trace("w", partial(self.controls_handler, v))
        self.x_scale = Spinbox(self.controls_region, from_=0, to=99, width=5, textvariable=v)
        self.x_scale.pack(side=RIGHT)

        v = StringVar()
        v.set("values 0")
        v.trace("w", partial(self.controls_handler, v))
        x_values_list = ["values %d" % i for i in range(2)]
        OptionMenu(self.controls_region, v, *x_values_list).pack(side=RIGHT)

        # urk - use the pack-regions-that-should-stay-visible-on-window-resize-first hack
        self.controls_region.pack(side=BOTTOM, fill=X, expand=1)
        self.xy_plot.pack(fill=BOTH, expand=1)
        self.plot_region.pack(fill=BOTH, expand=1)
        
    def controls_handler(self, v, *ign):
        print v.get()

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
        child_widget.config(scrollregion=(0, 0, child_widget.width, child_widget.height),
                            xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)

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

    def pack(self, *args, **kwargs):
        Canvas.pack(self,  *args, **kwargs)
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
