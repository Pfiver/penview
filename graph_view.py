# encoding: utf-8

from Tkinter import *
from itertools import izip
from functools import partial

from penview import *

class XYPlot(Canvas):
    "a custom canvas to display xy-plots"

    def __init__(self, parent, window, width, height):
        Canvas.__init__(self, parent, width=width, height=height, bg="#eef")

        self.window = window
        self.width, self.height = width, height

        self.upd = 1                                # units per division
        self.ppd = 100                              # pixel per division

        self.upds = {}
        self.lines = {}                             # this is a dict of dicts to which the keys are an ExperimentView and a values index

        self.axlines = ()

        window.conf.add_ox_listener(window.tk_cb(self.ox_update))
        window.conf.add_scale_listener(window.tk_cb(self.scale_update))

    def add_line(self, view, index):
        # plot a line for the values at index, against view.x_values and keep track of it
        #  color is determined by the view
        #  values_upd is determined by the conf
        #  values are taken from the experiment associated with the view
        conf = self.window.conf
        self.lines[view][index] = \
            self.data_line(view.ox.values[conf.x_values], view.ox.values[index],
                           x_upd=self.upds[conf.x_values], y_upd=self.upds[index], fill=view.colors[index])

    def remove_line(self, view, index):
        # delete the line that has been plotted for the values at index and loose track of it
        self.delete(self.lines[view][index])
        del self.lines[view][index]

    def ox_update(self, conf):

        scales_reset = False                                    # reset the scales only once; False -> not yet done

        for view in conf.ox_views(self.window):
            if view not in self.lines:                          # find added experiments, add our view_listener and call it once to display them
                if not scales_reset:
                    scales_reset = True
                    conf.reset_scales(self)
                    self.upds = conf.values_upd.copy()
                if view not in self.lines:                      # if the x-scale has changed, it might have been already added just above
                                                                # via reset_scales(), which is calling our scale_update() listener
                    self.lines[view] = {}                       # a dictionary containing all lines we have plotted
                    self.view_update(view)
                view.add_listener(self.window.tk_cb(self.view_update))

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

    def x_update(self, conf):   
        self.clear()                                            # if we plot against different x_values, we have to start over
        for view in conf.ox_views(self.window):
            self.lines[view] = {}                               # self.lines holds a dictionary containing all lines we have plotted
            self.view_update(view)

    def scale_update(self, conf):
        for i in self.upds:
            if self.upds[i] != conf.values_upd[i]:
                self.upds[i] = conf.values_upd[i]
                if i == conf.x_values:                          # if the x-scale has changed, we have to redraw every single line
                    self.clear()
                    for view in conf.ox_views(self.window):     # if this function is called from conf.reset_scales() it might
                        self.lines[view] = {}                   # _add_ the lines for this view to the self.lines dict here; see ox_update
                        self.view_update(view)
                    break                                       # next - otherwise an y-scale has changed
                for view in self.lines:                         # FIXME: seems slow
                    if i in view.y_values:                      # redraw only those that are visible
                        self.remove_line(view, i)
                        self.add_line(view, i)

        self.bbox = conf.bounding_box(self)
        xmin, ymin, xmax, ymax = self.bbox
        # if the bounding box is higher or wider then 1000 times ppd, protect ourselves from performance shame
        # the tk widget is not very well suited to quickly draw arbitrary pixels on the (off-)screen, at least not on a canvas,
        # because each call has to be translated to the corresponding tcl script string...
        # if self.bbox
        if xmax-xmin < 1000 * self.ppd and ymax-ymin < 1000 * self.ppd:
            self.redraw_axes()
        # translate the conventional to the canvas cordinate system
        self.config(scrollregion=(xmin, self.height - ymax, xmax, self.height - ymin))

    def view_update(self, view):
        for index in range(view.ox.nvalues + 1):                # loop over all values (indexes)
            if index == self.window.conf.x_values:              # if the values are used as the x_axis
                continue                                        # next - otherwise, these are y-values
            if index not in view.y_values:                      # if the values should not be displayed
                if index in self.lines[view]:                   # but are currently visible
                    self.remove_line(view, index)               # hide them
                continue                                        # next - otherwise these values ARE supposed to be visible
            if index not in self.lines[view]:                   # if the values are currently not visible
                self.add_line(view, index)                      # display them
                continue                                        # next - otherwise these values ARE supposed to be and WERE already visible

            if self.itemcget(self.lines[view][index], "fill") != view.colors[index]:    # if the color has changed
                self.itemconfig(self.lines[view][index], fill=view.colors[index])       # change the color

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
        # translate the conventional to the canvas cordinate system
        # using a generator expression avoids many copy operations
        return self.create_line(list((x, self.height - y) for x, y in points), **kwargs)

    def data_line(self, xlist, ylist, x_upd, y_upd, **kwargs):
        """
        plot the points in ylist against the those in xlist
        scale the coordinate axes by y_upd and x_upd respectively
        """
        xscale = lambda x: x / float(x_upd) * self.ppd
        yscale = lambda y: y / float(y_upd) * self.ppd

        # using izip and generator expressions avoids unnecessarily copying the data
        return self.draw_line(izip((xscale(x) for x in xlist), (yscale(y) for y in ylist)), **kwargs)

    def _draw_axes(self, color, grid_color):
        xmin, ymin, xmax, ymax = (self.ppd * (v // self.ppd) for v in self.bbox)
        xmax += self.ppd
        ymax += self.ppd

        for x in range(xmin + self.ppd, xmax, self.ppd):
            yield self.draw_line(((x, ymin), (x, ymax)), width=1, fill=grid_color)
            yield self.draw_line(((x, -3), (x, 3)), width=1, fill=color)

        for y in range(ymin + self.ppd, ymax, self.ppd):
            yield self.draw_line(((xmin, y), (xmax, y)), width=1, fill=grid_color)
            yield self.draw_line(((-3, y), (3, y)), width=1, fill=color)

        yield self.draw_line(((xmin, 0), (xmax, 0)), width=1, fill=color)
        yield self.draw_line(((0, ymin), (0, ymax)), width=1, fill=color)

    def redraw_axes(self, color="black", grid_color="gray"):
        map(self.delete, self.axlines)
        self.axlines = tuple(self._draw_axes(color, grid_color))

class PlotControls(Frame):
    def __init__(self, parent, window):
        Frame.__init__(self, parent)

        self.window = window
        self.labels = {}
        self.scalers = {}
        self.xchooser = None

        self.iscale = False     # This variable is used to prevent race conditions when the scale is updated
                                # The (prevetion) mechanism depends on there being no context switch between the two listeners/handlers
                                # This is achieved by the "if current_thread() == self:" test at the top of in PVWindow.tk_do() in window.py
                                # Probably it could be achieved by not wrapping self.scale_update() into window.tk_do() in the first place,
                                # but this everything CAN be wrapped and we don't have to worry

        window.conf.add_ox_listener(window.tk_cb(self.ox_update))
        window.conf.add_scale_listener(window.tk_cb(self.scale_update))

    def ox_update(self, conf):
        if len(conf.open_experiments):
            self.update_controls(conf)

    def scale_update(self, conf):
        if self.iscale:
            return
        for i in conf.values_upd:
            self.scalers[i].delete(0, len(self.scalers[i].get()))
            self.scalers[i].insert(0, conf.values_upd[i])

    def sb_handler(self, i, *ign):
        try:
            scale = float(self.scalers[i].get())
        except:
            return
        if scale == 0:
            scale = 0.001
            self.scalers[i].delete(0, len(self.scalers[i].get()))
            self.scalers[i].insert(0, scale)
        self.iscale = True
        self.window.conf.set_scale(i, scale)
        self.iscale = False

    def sw_handler(self, i, event):
        scale = self.window.conf.values_upd[i]
        inc = self.scalers[i].config("increment")[4]
        scale += {4: inc, 5: -inc}[event.num]                   # button 4 => up; button 5 => down
        scale = int(scale)
        if scale == 0:
            scale = 0.001
        self.scalers[i].delete(0, len(self.scalers[i].get()))
        self.scalers[i].insert(0, scale)
        self.iscale = True
        self.window.conf.set_scale(i, scale)
        self.iscale = False

    def xv_handler(self, *ignored):
        print "x"

    def update_controls(self, conf):
        # controls_region setup - keep pack()ing order !

        # dispose old controls
        for l in self.labels.values(): l.pack_forget()           # FIXME: we should reuse those widgets - shouldn't we ?
        for s in self.scalers.values(): s.pack_forget()          #        but currently I have no time to code the housekeeping logic
        if self.xchooser:
            self.xchooser.pack_forget()

        # create y-axis controls
        for i in range(1, conf.nvalues + 1):
            sb = Spinbox(self, from_=0, to=99999, width=5, command=partial(self.sb_handler, i))
            sb.pack(side=LEFT)
            self.scalers[i] = sb
            sb.bind("<Button-4>", partial(self.sw_handler, i))
            sb.bind("<Button-5>", partial(self.sw_handler, i))
            sb.bind("<KeyRelease>", partial(self.sb_handler, i))

            ul = Label(self, text=conf.units[i]+"/div")
            ul.pack(side=LEFT)
            self.labels[i] = ul

        # create x-axis controls
        xunits = conf.units[conf.x_values]

        self.labels[0] = Label(self, text=xunits+"/div")
        self.labels[0].pack(side=RIGHT)

        sb = Spinbox(self, from_=0, to=99999, width=5, command=partial(self.sb_handler, 0))
        # keep the order here - trace() v AFTER using it for Spinbox()
        sb.pack(side=RIGHT)
        self.scalers[0] = sb
        sb.bind("<Button-4>", partial(self.sw_handler, 0))
        sb.bind("<Button-5>", partial(self.sw_handler, 0))
        sb.bind("<KeyRelease>", partial(self.sb_handler, 0))

        v = StringVar()
        v.set("Zeit")
        v.trace("w", partial(self.xv_handler, v))
        x_values_list = ["Zeit"]
  
        for i in range(min([ox.nvalues for ox in conf.open_experiments])):
            desc = ""
            for vdesc in [ox.get_desc(i + 1) for ox in conf.open_experiments]:
                if not desc.startswith(vdesc):
                    desc += " (%s)" % vdesc
            x_values_list.append(vdesc)

        self.xchooser = OptionMenu(self, v, *x_values_list)
        self.xchooser.v = v
        self.xchooser.pack(side=RIGHT)

        # helps !
        #  to make make the xyplot canvas initially be resized properly
        #  -> reset_values_upd() setting proper scales -> xyplot bounding box matching canvas size/scroll region  
        self.window.tk.update_idletasks()

class ScrollRegion(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.xscrollbar = Scrollbar(self, orient=HORIZONTAL)
        self.yscrollbar = Scrollbar(self, orient=VERTICAL)
        self.xscrollbar.grid(row=1, column=0, sticky=E+W)
        self.yscrollbar.grid(row=0, column=1, sticky=N+S)

    def scroll_child(self, child_widget):
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
        child_widget.bind("<Button-1>", self.b1_handler)
        child_widget.bind("<Button1-Motion>", self.b1m_handler)
        child_widget.bind("<ButtonRelease-1>", self.b1r_handler)

    def b1_handler(self, e):
        self.config(cursor="fleur")
        self.mark = e
        self.child_widget.scan_mark(e.x, e.y)
        
    def b1m_handler(self, e):
        self.child_widget.scan_dragto(self.mark.x + (e.x-self.mark.x)/10,
                                      self.mark.y + (e.y-self.mark.y)/10)

    def b1r_handler(self, e):
        self.config(cursor="arrow")

    def ywheel_handler(self, e):
        self.child_widget.yview_scroll({4: -1, 5: 1 }[e.num], 'units') # button 4 => up; button 5 => down

    def xwheel_handler(self, e):
        self.child_widget.xview_scroll({6: -1, 7: 1 }[e.num], 'units') # button 6 => left; button 7 => right # FIXME: correct ???
