# encoding: utf-8

from Tkinter import *
from itertools import izip
from functools import partial

from penview import *
from recipe_52266 import MultiListbox

class DataRegion(Frame):
    def __init__(self, parent, conf):
        Frame.__init__(self, parent)

        self.conf = conf

        conf.add_viewmode_listener(self.viewmode_update)

        self.controls_region = PlotControls(self, self.conf)
        self.plot_region = ScrollRegion(self)

        self.xy_plot = XYPlot(self.plot_region, conf, 800, 600)
        self.xy_plot.pack(fill=BOTH, expand=1)

#        self.table_region = PVTable(self, self.conf)

    def show_table(self):
        self.conf.ui.controller.q(PVAction.show_graph)
        raise Exception("Sorry, table view is not yet implemented")

        self.plot_region.pack_forget()          # FIXME: on the first call the widgets are not yet packed
        self.controls_region.pack_forget()

        self.table_region.pack(fill=BOTH, expand=YES)

    def show_plot(self):
#        self.table_region.pack_forget()          # FIXME: on the first call the widget is not yet packed

        # urk - use the pack-regions-that-should-stay-visible-on-window-resize-first hack
        self.controls_region.pack(side=BOTTOM, fill=X, expand=0)
        self.plot_region.pack(fill=BOTH, expand=1)

    def viewmode_update(self, conf):
        show = { XYPlot: self.show_plot,
                 PVTable: self.show_table}
        show[conf.viewmode]()

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
    class Origin:
        def __init__(self, x, y):
            self.x = x
            self.y = y
        def set_origin(self, x, y):
            self.x = x
            self.y = y

    def __init__(self, parent, conf, width, height):
        self.origin = XYPlot.Origin(0, 0)
        self.upd = 1                                # units per division
        self.ppd = 100                              # pixel per division
        self.conf = conf
        self.parent = parent
        self.width, self.height = width, height

        self.fgcolor = "black"
        self.bgcolor = "#EEEEEE"
        Canvas.__init__(self, self.parent, bg=self.bgcolor,
                              width=self.width, height=self.height)

        self.draw_axes(self.fgcolor)
        self.bind('<Configure>', self.resize_handler)

        self.upds = {}
        self.lines = {}                             # this is a dict of dicts to which the keys are an ExperimentView and a values index

        conf.add_ox_listener(self.ox_update)
        conf.add_scale_listener(self.scale_update)

    def add_line(self, view, index):
        # plot a line for the values at index, against view.x_values and keep track of it
        #  color is determined by the view
        #  values_upd is determined by the conf
        #  values are taken from the experiment associated with the view
        self.lines[view][index] = \
            self.data_line(view.ox.values[self.conf.x_values], view.ox.values[index],
                           x_upd=self.conf.values_upd[self.conf.x_values], y_upd=self.conf.values_upd[index], fill=view.colors[index])
        # it works both ways and I'm not 100% sure now which is the right one 
        #                   x_upd=view.ui.conf.values_upd[view.ui.conf.x_values], y_upd=view.ui.conf.values_upd[index], fill=view.colors[index])

    def remove_line(self, view, index):
        # delete the line that has been plotted for the values at index and loose track of it

        self.delete(self.lines[view][index])
        del self.lines[view][index]

    def ox_update(self, conf):
        # reset scale to a sane default (all data visible)
        self.upds = {}
        self.origin.set_origin(*conf.reset_upd(self.ppd, self.width, self.height))
        self.upds = conf.values_upd.copy()

        for ox in conf.open_experiments:           
            view = ox.views[self.conf.ui]
            if view not in self.lines:              # find added experiments, add our view_listener and call it once to display them
                self.lines[view] = {}               # a dictionaray containing all lines we have plotted
                self.view_update(view)
                view.add_listener(self.view_update)

        # from http://effbot.org/zone/python-list.htm:
        #  Note that the for-in statement maintains an internal index, which is incremented for each loop iteration.
        #  This means that if you modify the list you’re looping over, the indexes will get out of sync, and you may
        #  end up skipping over items, or process the same item multiple times.
        #  To work around this, you can loop over a copy of the list: 
        # Seems to hold true for dicts as well. If you don't get a copy of the keys
        # using dict.keys() and modify the dict in the loop, a RuntimeError is raised
        for view in self.lines.keys():
            if view.ox not in conf.open_experiments:
                for index in self.lines[view]:
                    self.delete(self.lines[view][index])
                del self.lines[view]
                

    def scale_update(self, conf):
        for i in self.upds:
            if self.upds[i] != conf.values_upd[i]:
                self.upds[i] = conf.values_upd[i]
                if i == conf.x_values:                  # if the x-scale has changed, we have to redraw every single line
                    self.clear()
                    for ox in conf.open_experiments:           
                        view = ox.views[self.conf.ui]
                        self.lines[view] = {}
                        self.view_update(view)
                    return                              # next - otherwise an y-scale has changed
                for view in self.lines:                 # FIXME: seems slow
                    self.remove_line(view, i)
                    self.add_line(view, i)

    def x_update(self, conf):   
        self.clear()            # if we plot against different x_values, we have to start over
        for ox in conf.open_experiments:           
            view = ox.views[self.conf.ui]
            self.lines[view] = {}               # a dictionaray containing all lines we have plotted
            self.view_update(view)

    def view_update(self, view):
        for index in range(view.ox.get_nvalues() + 1):      # loop over all values (indexes)
            if index == self.conf.x_values:                 # if the values are used as the x_axis
                continue                                    # next - otherwise these are y-values
            if index not in view.y_values:                  # if the values should not be displayed
                if index in self.lines[view]:               # but are currently visible
                    self.remove_line(view, index)           # hide them
                continue                                    # next - otherwise these values ARE supposed to be visible
            if index not in self.lines[view]:               # if the values are currently not visible
                self.add_line(view, index)                  # display them
                continue                                    # next - otherwise these values ARE supposed to be and WERE already visible
            if self.itemcget(self.lines[view][index], "fill") != view.colors[index]:    # if the color has changed
                self.itemconfig(self.lines[view][index], fill=view.colors[index])       # change the color

    def pack(self, *args, **kwargs):
        Canvas.pack(self,  *args, **kwargs)
        if self.parent.__class__ == ScrollRegion:
            self.parent.child_added(self)

    def clear(self):
        for view in self.lines.keys():
            for index in self.lines[view]:
                self.delete(self.lines[view][index])
            del self.lines[view]

    def draw_line(self, points, **kwargs):
        """
        draw a line along a list of point coordinates
        :parameters:
            points    list of point coordinates in the form: ((x1, y1), (x2, y2))
        """
        # using a generator expression avoids many copy operations
        return self.create_line(list((x, self.height - y) for x, y in points), **kwargs)

    def data_line(self, xlist, ylist, x_upd, y_upd, **kwargs):
        """
        plot the points in ylist against the those in xlist
        scale the coordinate axes by y_upd and x_upd respectively
        """
        xscale = lambda x: x / float(x_upd) * self.ppd + self.origin.x
        yscale = lambda y: y / float(y_upd) * self.ppd + self.origin.y

        # using izip and generator expressions avoids many copy operations
        return self.draw_line(izip((xscale(x) for x in xlist), (yscale(y) for y in ylist)), **kwargs)

    def draw_axes(self, color="black"):
        O = self.origin
        # positive axes
        self.draw_line(((O.x, O.y), (self.width, O.y)), width=1, fill=color)
        self.draw_line(((O.x, O.y), (O.x, self.height)), width=1, fill=color)
        for x in range(O.x, self.width, self.ppd):
            self.draw_line(((x, O.y - 3), (x, O.y + 3)))
        for y in range(O.y, self.height, self.ppd):
            self.draw_line(((O.x - 3, y), (O.x + 3, y)))
        # negative axes
        self.draw_line(((O.x, O.y), (0, O.y)), width=1, fill=color)
        self.draw_line(((O.x, O.y), (O.x, 0)), width=1, fill=color)
        for x in range(O.x, 0, -self.ppd):
            self.draw_line(((x, O.y - 3), (x, O.y + 3)))
        for y in range(O.y, 0, -self.ppd):
            self.draw_line(((O.x - 3, y), (O.x + 3, y)))

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

        self.conf = conf
        self.iscale = False
        self.labels = {}
        self.scalers = {}
        self.xchooser = None

        conf.add_ox_listener(self.ox_update)
        conf.add_scale_listener(self.scale_update)

    def ox_update(self, conf):
        if len(conf.open_experiments):
            self.update_controls(conf)

    def scale_update(self, conf):
        if self.iscale:
            return
        iscale = True
        for i in conf.values_upd:
            self.scalers[i].v.set(conf.values_upd[i])
        iscale = False

    def controls_handler(self, v, i, *ign):
        if self.iscale:
            return
        self.iscale = True
        try: self.conf.set_scale(i, v.get())
        except: pass
        self.iscale = False

    def update_controls(self, conf):
        # controls_region setup - keep pack()ing order !
        # y-axis controls

        for l in self.labels.values(): l.pack_forget()           # FIXME: uuuurg - we should reuse those widgets - shouldn't we ?
        for s in self.scalers.values(): s.pack_forget()          #        but currently I have no time to code the housekeeping logic
        if self.xchooser:
            self.xchooser.pack_forget()

        view = conf.open_experiments[0].views[conf.ui]

        # y-axis controls
        for i in range(conf.nvalues):
            v = DoubleVar()
            sb = Spinbox(self, from_=0, to=99999, width=5, textvariable=v)
            # keep the order here - trace() v AFTER using it for Spinbox()
            v.trace("w", partial(self.controls_handler, v, i+1))
            sb.v = v
            sb.pack(side=LEFT)
            self.scalers[i+1] = sb

            ul = Label(self, text=conf.units[i])
            ul.pack(side=LEFT)
            self.labels[i+1] = ul

        # x-axis controls
        if conf.x_values == 0:      # time on x-axis
            xunits = "s"
        else:
            xunits = conf.units[conf.x_values-1]    # because time is always "s", conf.units key "0" refers to the v1_unit metadata variable

        self.labels[0] = Label(self, text=xunits)
        self.labels[0].pack(side=RIGHT)

        v = DoubleVar()
        self.scalers[0] = Spinbox(self, from_=0, to=99999, width=5, textvariable=v)
        # keep the order here - trace() v AFTER using it for Spinbox()
        v.trace("w", partial(self.controls_handler, v, 0))
        self.scalers[0].v = v
        self.scalers[0].pack(side=RIGHT)

        v = StringVar()
        v.set("Zeit")
        v.trace("w", partial(self.controls_handler, v))
        x_values_list = ["Zeit"]
  
        for i in range(min([ox.get_nvalues() for ox in conf.open_experiments])):
            desc = ""
            for vdesc in [ox.get_desc(i + 1) for ox in conf.open_experiments]:
                if not desc.startswith(vdesc):
                    desc += " (%s)" % vdesc
            x_values_list.append(vdesc)

        self.xchooser = OptionMenu(self, v, *x_values_list)
        self.xchooser.v = v
        self.xchooser.pack(side=RIGHT)
    
class PVTable(MultiListbox):
    def __init__(self, parent, conf):
        self.parent = parent
        MultiListbox.__init__(self, self.parent, ("No Data",)) # Workaround for first call error: "AttributeError: PVTable instance has no attribute 'tk'"
        conf.add_ox_listener(self.ox_update)
 
    def ox_update(self, conf):
        headers = ["Zeit",]
        data = []
        for ox in conf.open_experiments:
            # HEADER
            ox.header = self.get_header(ox)
            print "ox.header: %s" % ox.header
            for header in ox.header:
                headers.append(header)
            # DATA(s)
            print len(self.get_data(ox))
            for j in range(len(self.get_data(ox))):
#                print "self.get_data(ox)[%d]:" % j
#                print self.get_data(ox)[j]
                data.append(self.get_data(ox)[j])
#        print "calling update_table(headers, data): %s, %s" % (headers, data)
        self.update_table(headers, data)
        
    def get_header(self, ox):
        # Add Description (Table Header)
        header = []
        for i in range(ox.get_nvalues()):
            header.append( ox.get_desc(i), )
        return header

    def get_data(self, ox):
        data = []
        self.cols = ox.get_nvalues() # get the count of columns
        self.rows = len(ox.values[1]) # get the length of v1 values (v1 exists!)
        # Add Data from Experiment Table
        for row in range(self.rows):
#            print "ox.sqlvalues[%s]: %s " % ( row, ox.sqlvalues[row] )
            data.append(ox.sqlvalues[row],)
        return data
                
    def update_table(self, header, data):
        MultiListbox.__init__(self, self.parent, header)
#        print "data: %s" % data
        for row in range(len(data)):
#            print "row: %s " % row
            self.insert(END, data[row])
