from Tkinter import *
from itertools import chain
from functools import partial

from penview import *
from recipe_52266 import MultiListbox

class DataRegion(Frame):
    def __init__(self, parent, pvconf, ctrl):
        Frame.__init__(self, parent)
        self.conf = pvconf
        self.controller = ctrl
        self.xy_plot = None
        self.plot_region = None
        self.table_region = None

        pvconf.add_ox_listener(self.ox_update)
        pvconf.add_view_listener(self.view_update)

    def ox_update(self, conf):
        self.update()
        
        
    def view_update(self, conf):
        view_method = { XYPlot: self.show_plot,
                        PVTable: self.show_table}
        view_method[conf.view]()

    def show_table(self):
        if self.plot_region:                        # TODO: ev. weiterer wrapper frame um plot+controls _region
            self.plot_region.pack_forget()          # plot_region can't exist without controls_region
            self.controls_region.pack_forget()

        if not self.table_region:
            self.table_region = PVTable(self)

        self.table_region.pack(fill=BOTH, expand=YES)

    def show_plot(self):
        if self.table_region:
            self.table_region.pack_forget()

        if not self.plot_region:
            self.plot_region = ScrollRegion(self)
            self.controls_region = Frame(self)

            self.xy_plot = XYPlot(self.plot_region, 800, 600) # custom canvas widget
            self.xy_plot.pack(fill=BOTH, expand=1)

############# auslagern
#
            # controls_region setup - keep pack()ing order !
            # y-axis controls 
            self.y_scales = []
            self.y_units = []
            for i in range(2):
                v = StringVar()
                v.trace("w", partial(self.controls_handler, v))
                sb = Spinbox(self.controls_region, from_=0, to=99, width=5, textvariable=v)
                sb.v = v
                sb.pack(side=LEFT)
                self.y_scales.append(sb)
    
                ul = Label(self.controls_region, text="y%d units" % i)
                ul.pack(side=LEFT)
                self.y_units.append(ul)
    
            # x-axis controls
            self.x_units = Label(self.controls_region, text="x units")
            self.x_units.pack(side=RIGHT)
    
            v = StringVar()
            v.trace("w", partial(self.controls_handler, v))
            self.x_scale = Spinbox(self.controls_region, from_=0, to=99, width=5, textvariable=v)
            self.x_scale.v = v
            self.x_scale.pack(side=RIGHT)
    
            v = StringVar()
            v.set("values 0")
            v.trace("w", partial(self.controls_handler, v))
            x_values_list = ["values %d" % i for i in range(2)]
            self.x_values = OptionMenu(self.controls_region, v, *x_values_list)
            self.x_values.v = v
            self.x_values.pack(side=RIGHT)
#
############# bis hier

        # urk - use the pack-regions-that-should-stay-visible-on-window-resize-first hack
        self.controls_region.pack(side=BOTTOM, fill=X, expand=1)
        self.plot_region.pack(fill=BOTH, expand=1)

# for testing - better place to be found
#        self.update()
        
    def controls_handler(self, v, *ign):
#        print v.get()
        pass
    
    def update(self):
        debug(str(self.conf.values_upd))
        x0 = self.conf.open_experiments[0]
        self.x_scale.v.set(self.conf.values_upd[x0.perspective.xaxis_values])
        for i in range(self.conf.open_experiments[0].get_nvalues()):
            self.y_scales[i].v.set(self.conf.values_upd[i + 1])
        for ox in self.conf.open_experiments:
            for index in ox.perspective.yaxis_values:
                self.xy_plot.plot_data(ox.values[ox.perspective.xaxis_values], ox.values[index],
                                       self.conf.values_upd[ox.perspective.xaxis_values], self.conf.values_upd[index])

#        self.xy_plot.plot_data(range(100), range(100), 4, 8)

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
        self.upd = 1                                # units per division
        self.ppd = 100                              # pixel per division
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

    def line(self, points, **kwargs):
        """
        draw a line along a list of point coordinates
        :parameters:
            points    list of point coordinates in the form: ((x1, y1), (x2, y2))
        """

        args = []
        for p in points:
            args.append(p[0])          
            args.append(self.height - p[1])

        self.create_line(*args, **kwargs)

    def draw_axes(self, _color="black"):
        class O:
            x = 0
            y = 0
        self.line(((O.x, O.y), (self.width, O.y)), width=1, fill=_color)
        self.line(((O.x, O.y), (O.x, self.height)), width=1, fill=_color)
        for x in range(0, self.width, self.ppd):
            self.line(((x, O.y - 3), (x, O.y + 3)))
        for y in range(0, self.height, self.ppd):
            self.line(((O.x - 3, y), (O.x + 3, y))) 

    def plot_data(self, x, y, x_upd, y_upd):
        x_upd += 0.0
        y_upd += 0.0
        x = map(lambda v: v / x_upd * self.ppd, x)
        y = map(lambda v: v / y_upd * self.ppd, y)
        self.line(zip(x, y), fill=self.fgcolor)

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

class PVTable(MultiListbox):
    def __init__(self, parent):
        MultiListbox.__init__(self, parent, (('Subject', 40), ('Sender', 20), ('Date', 10)))
        for i in range(1000):
            self.insert(END, ('Important Message: %d' % i, 'John Doe', '10/10/%04d' % (1900+i)))