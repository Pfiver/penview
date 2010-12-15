from Tkinter import *

class DataRegion(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        
        self.plot_region = ScrollRegion(self)
        self.xy_plot = XYPlot(self.plot_region, 800, 600) # custom canvas widget
        
        self.controls_region = Frame(self)

        self.y_scales = [Spinbox(self.controls_region) for i in range(2)]
        self.y_units = [Label(self.controls_region, text="y%d units" % i) for i in range(2)]

        self.x_chosen = StringVar()
        self.x_chosen.set("values 0")
        self.x_chooser = OptionMenu(self.controls_region, self.x_chosen, ["values %d" % i for i in range(2)])

        self.x_scale = Spinbox(self.controls_region)
        self.x_units = Label(self.controls_region, text="x units")
        
        for i in range(2):
            self.y_scales[i].pack(side=LEFT)
            self.y_units[i].pack(side=LEFT)
        
        self.x_units.pack(side=RIGHT)
        self.x_scale.pack(side=RIGHT)
        self.x_chooser.pack(side=RIGHT)

        self.xy_plot.pack(fill=BOTH, expand=1)
        self.plot_region.pack(fill=BOTH, expand=1)
        self.controls_region.pack(fill=X, expand=1)

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
        child_widget.config(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set,
                            scrollregion=(0, 0, child_widget.width, child_widget.height))

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
