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

        pvconf.add_ox_listener(self.ox_update)
        pvconf.add_view_listener(self.view_update)

        self.controls_region = PlotControls(self, self.conf)
        self.plot_region = ScrollRegion(self)

        self.xy_plot = XYPlot(self.plot_region, 800, 600)
        self.xy_plot.pack(fill=BOTH, expand=1)

        self.table_region = PVTable(self)

    def show_table(self):
        self.plot_region.pack_forget()          # FIXME: on the first call the widgets are not yet packed
        self.controls_region.pack_forget()

        self.table_region.pack(fill=BOTH, expand=YES)

    def show_plot(self):
        self.table_region.pack_forget()          # FIXME: on the first call the widget is not yet packed

        # urk - use the pack-regions-that-should-stay-visible-on-window-resize-first hack
        self.controls_region.pack(side=BOTTOM, fill=X, expand=1)
        self.plot_region.pack(fill=BOTH, expand=1)
        
    def ox_update(self, conf):

#        debug(str(conf.values_upd))
        x0 = conf.open_experiments[0]

#        self.x_scale.v.set(conf.values_upd[x0.perspective.xaxis_values])
#        for i in range(conf.open_experiments[0].get_nvalues()):
#            self.y_scales[i].v.set(self.conf.values_upd[i + 1])

#        for ox in self.conf.open_experiments:
#            for index in ox.perspective.yaxis_values:
#                self.xy_plot.plot_data(ox.values[ox.perspective.xaxis_values], ox.values[index],
#                                       self.conf.values_upd[ox.perspective.xaxis_values], self.conf.values_upd[index])

        self.xy_plot.plot_data(range(100), range(100), 4, 8)

    def view_update(self, conf):
        view_method = { XYPlot: self.show_plot,
                        PVTable: self.show_table}
        view_method[conf.view]()

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
        self.child_widget = child_widget
        self.xscrollbar.config(command=child_widget.xview)
        self.yscrollbar.config(command=child_widget.yview)
        child_widget.grid(row=0, column=0, sticky=N+S+E+W)
        child_widget.config(scrollregion=(0, 0, child_widget.width, child_widget.height),
                            xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)

        child_widget.bind("<Button-4>", self.ywheel_handler)
        child_widget.bind("<Button-5>", self.ywheel_handler)
#        child_widget.bind("<Button-6>", self.xwheel_handler)    # FIXME: fix tkinter ?
#        child_widget.bind("<Button-7>", self.xwheel_handler)

    def ywheel_handler(self, e):
        self.child_widget.yview_scroll({4: -1, 5: 1 }[e.num], 'units') # button 4 => up; button 5 => down
    def xwheel_handler(self, e):
        self.child_widget.xview_scroll({6: -1, 7: 1 }[e.num], 'units') # button 6 => left; button 7 => right # FIXME: correct ???

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

class PlotControls(Frame):
    def __init__(self, parent, conf):
        Frame.__init__(self, parent)
        
        self.labels = {}
        self.scalers = {}
        self.xchooser = None

        conf.add_ox_listener(self.update_ox)
        conf.add_scale_listener(self.update_scales)

    def update_ox(self, conf):
        if len(conf.open_experiments):
            self.update_controls(conf)

    def update_scales(self, conf):
        for i in conf.values_upd:
            self.scalers[i].v.set(conf.values_upd[i])

    def update_controls(self, conf):
        # controls_region setup - keep pack()ing order !
        # y-axis controls

        for l in self.labels.values(): l.pack_forget()           # FIXME: uuuurg - we should reuse those widgets - shouldn't we ?
        for s in self.scalers.values(): s.pack_forget()          #        but currently I have no time to code the housekeeping logic
        if self.xchooser:
            self.xchooser.pack_forget()

        ppct = conf.open_experiments[0].perspective

        # y-axis controls
        for i in range(conf.nvalues):
            v = StringVar()
            v.trace("w", partial(self.controls_handler, v))
            sb = Spinbox(self, from_=0, width=5, textvariable=v)
            sb.v = v
            sb.pack(side=LEFT)
            self.scalers[i+1] = sb

            ul = Label(self, text=conf.units[i])
            ul.pack(side=LEFT)
            self.labels[i+1] = ul

        # x-axis controls
        if ppct.x_values == 0:      # time on x-axis
            xlabel = "s"
        else:
            xlabel = conf.units[ppct.x_values-1]    # because time is allways "s", ppct.units key "0" is v1_unit

        self.labels[0] = Label(self, text="s")
        self.labels[0].pack(side=RIGHT)

        v = StringVar()
        v.trace("w", partial(self.controls_handler, v))
        self.scalers[0] = Spinbox(self, from_=0, width=5, textvariable=v)
        self.scalers[0].v = v
        self.scalers[0].pack(side=RIGHT)

        v = StringVar()
        v.set("Zeit")
        v.trace("w", partial(self.controls_handler, v))
        x_values_list = ["Zeit"]
  
        for i in range(min([ox.get_nvalues() for ox in conf.open_experiments])):
            desc = ""
            for vdesc in [ox.get_desc(i) for ox in conf.open_experiments]:
                if not desc.startswith(vdesc):
                    desc += " (%s)" % vdesc
            x_values_list.append(vdesc)

        self.xchooser = OptionMenu(self, v, *x_values_list)
        self.xchooser.v = v
        self.xchooser.pack(side=RIGHT)

    def controls_handler(self, v, *ign):
#        debug( v.get() )
        pass
    
class PVTable(MultiListbox):
    def __init__(self, parent):
        MultiListbox.__init__(self, parent, ('Subject', 'Sender', 'Date'))
        for i in range(1000):
            self.insert(END, ('Item %d' % i, 'John Doe %d' % i, '%04d' % i))