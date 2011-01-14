# encoding: utf-8

from Tkinter import *
from itertools import izip
from functools import partial

from penview import *

class XYPlot(Canvas):
    "a custom canvas to display xy-plots"

    def __init__(self, parent, window, width, height):
        
        self.canvas_color = "#eef"

        # ouff
        #
        # One most annoying spacing issue arises from the fact that highlightthickness doesn't default to 0
        # for canvas widgets (and maybe others). The problem is that the widgets winfo_width() / winfo_height():
        # will allways be 2*highlightthickness larger then the widget. This has implications especially when changing
        # the 'scrollregion' - e.g. if you whish to set it exactly to the size if the widget, you'd probably have to subtract
        # 2*highlightthickness first. The easier solution is to set highlightthickness to 0.
        # Thanks to "papageno", for sharing this: http://www.tek-tips.com/viewthread.cfm?qid=1161244&page=26
        #
        Canvas.__init__(self, parent, width=width, height=height, bg=self.canvas_color, highlightthickness=0)
        #
        # on

        self.window = window
        self.width, self.height = width, height     # The original with and height - this is a static variable
                                                    # It is used by ScrollRegion to initially set the "scrollregion=" of this Canvas
                                                    # The original _height is _also used later on for all coordinate system translations

                                                    # When resizing the window, the original XYPlot Canvas is never destroyed.
                                                    # It is automatically resized by the pack()er (expand=YES, fill=BOTH) and
                                                    # the original (0,0) coordinates always stay where they are.
                                                    # This is also where the axes are allways plotted.

        self.ppd = 100                              # pixels per division

        self.upds = {}                              # the units per divisions we originally used to plot all self.lines
        self.lines = {}                             # this is a dict of dicts to which the keys are an ExperimentView and a values index

        self.axlines = ()                           # a tuple lst of all axis related lines currently visible on the canvas 

        window.conf.add_ox_listener(window.tk_cb(self.ox_update))
        window.conf.add_x_listener(window.tk_cb(self.x_update))
        window.conf.add_scale_listener(window.tk_cb(self.scale_update))

    def add_line(self, view, index):
        """
        plot a line for the values at index, against view.x_values and keep track of it
         color is determined by the view
         scale is taken from self.upds
         values are taken from the experiment associated with the view
        """
        conf = self.window.conf
        self.lines[view][index] = \
            self.data_line(view.ox.values[conf.x_values], view.ox.values[index],
                           x_upd=self.upds[conf.x_values], y_upd=self.upds[index], fill=view.colors[index])

    def remove_line(self, view, index):
        "delete the line that has been plotted for the values at index and loose track of it"
        self.delete(self.lines[view][index])
        del self.lines[view][index]

    def ox_update(self, conf):
        "PVConf.ox_listener callback function"

        for view in conf.ox_views():
            if view not in self.lines:                          # find added experiments, add our view_listener and call it once to plot the values
                for i, s in conf.values_upd.iteritems():        # if we haven't plotted this kind of values before, record the scale to use
                    if i not in self.upds:
                        self.upds[i] = s
                self._update_bbox()
                self.lines[view] = {}
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
        "PVConf.x_listener callback (stub)"
        self.clear()                                            # if we plot against different x_values, we have to start over
        for view in conf.ox_views():
            self.lines[view] = {}                               # self.lines holds a dictionary containing all lines we have plotted
            self.view_update(view)

    def scale_update(self, conf):
        "PVConf.scale_listener callback"
        for i in self.upds:
            if self.upds[i] != conf.values_upd[i]:
                self.upds[i] = conf.values_upd[i]
                if i == conf.x_values:                          # if the x-scale has changed, we have to redraw every single line
                    self.clear()
                    for view in conf.ox_views():                # if this function is called from conf.reset_scales() it might
                        self.lines[view] = {}                   # _add_ the lines for this view to the self.lines dict here; see ox_update
                        self.view_update(view)
                    break                                       # next - otherwise an y-scale has changed
                for view in self.lines:                         # FIXME: seems slow
                    if i in view.y_values:                      # redraw only those that are visible
                        self.remove_line(view, i)
                        self.add_line(view, i)

        self._update_bbox()

    def _update_bbox(self):
        self.bbox = xmin, ymin, xmax, ymax = self.window.conf.bounding_box(self)
        # if the bounding box is higher or wider then 1000 times ppd, protect ourselves from performance shame
        # the tk widget is not very well suited to quickly draw arbitrary pixels on the (off-)screen, at least not on a canvas,
        # because each call has to be translated to the corresponding tcl script string...
        if xmax-xmin < 1000 * self.ppd and ymax-ymin < 1000 * self.ppd:
            self.redraw_axes()
        # translate the conventional to the canvas cordinate system
        self.config(scrollregion=(xmin, self.height - ymax, xmax, self.height - ymin))

    def view_update(self, view):
        "ExperimentView.listener callback"
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
        "remove all lines from the canvas and empty the self.lines dictionary"
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
        """"
        a generator which draws all lines related to the axes and yields their references
            draws the axes so they fill the current self.bbox
        """
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
        "remove and redraw all lines related to the axes on the canvas"
        map(self.delete, self.axlines)
        self.axlines = tuple(self._draw_axes(color, grid_color))

class PlotControls(Frame):
    "The frame which holds all the scale adjust spinboxes as well as the x-axe chooser below the plot region"
    
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
        "PVConf.ox_listener callback function"
        if len(conf.open_experiments):
            self._update_controls(conf)

        for view in self.window.conf.ox_views():
            view.add_listener(self.window.tk_cb(self.view_update))


    def scale_update(self, conf):
        "PVConf.scale_listener callback function"
        if self.iscale:
            return
        for i in conf.values_upd:
            self.scalers[i].delete(0, len(self.scalers[i].get()))
            self.scalers[i].insert(0, conf.values_upd[i])

    def view_update(self, view):
        "ExperimentView.listener callback function"
        self._update_controls(self.window.conf)

    def sb_handler(self, i, *event):
        "scalers spinboxes 'action=' and '<KeyRelease>' event handler"
        try:
            scale = float(self.scalers[i].get())
        except:
            return
        if scale == 0:
            scale = 0.001
            # don't interfere if somebody is typing in a value like "0.5"
            # (type "3" is KeyRelease, see http://infohost.nmt.edu/tcc/help/pubs/tkinter/events.html#event-types)
            if not (len(event) > 0 and event[0].type == "3"):
                self.scalers[i].delete(0, len(self.scalers[i].get()))
                self.scalers[i].insert(0, scale)
        self.iscale = True
        self.window.conf.set_scale(i, scale)
        self.iscale = False

    def sw_handler(self, i, event):
        "scalers spinboxes scrollwheel event handler"
        scale = self.window.conf.values_upd[i]
        inc = self.scalers[i].config("increment")[4]
        adj = {4: inc, 5: -inc}[event.num]                  # button 4 => up; button 5 => down
        if scale < 1:                                       # FIXME: there is a lot of room for improvement here
            adj /= 50                                       # the adjustment adj should be computed much more dynamically  
        scale += adj
        if scale <= 0:
            scale = 0.001
        self.scalers[i].delete(0, len(self.scalers[i].get()))
        self.scalers[i].insert(0, scale)
        self.iscale = True
        self.window.conf.set_scale(i, scale)
        self.iscale = False

    def xv_handler(self, v, *ignored):
        "xchooser OptionMenu event handler (StringVar trace function)"
        self.window.conf.set_x_values(self.xchooser.vals[v.get()])
        self.window.do(PVAction.reset_scale)

    # private helper function
    def _update_controls(self, conf):
        "set up the controls_region"

        # don't change the pack()ing order in this function

        # dispose old controls
        for l in self.labels.values(): l.pack_forget()           # FIXME: we should reuse those widgets - shouldn't we ?
        for s in self.scalers.values(): s.pack_forget()          # ...but it might not be worth the effort to code the housekeeping logic
        if self.xchooser:
            self.xchooser.pack_forget()

        # create y-axis controls
        for i in range(conf.nvalues + 1):
            if i == conf.x_values:                         # these are the x-axis values
                continue                                        # next

            ## y-axis scaler
            sb = Spinbox(self, value=conf.values_upd[i], from_=0, to=99999, width=5, command=partial(self.sb_handler, i))
            sb.pack(side=LEFT)
            self.scalers[i] = sb
            sb.bind("<Button-4>", partial(self.sw_handler, i))      # concerning windows and mac scrollwheel handling,
            sb.bind("<Button-5>", partial(self.sw_handler, i))      # see the commment in the ScrollRegion class at the bottom of this file
            sb.bind("<KeyRelease>", partial(self.sb_handler, i))

            ## y-axis units label
            ul = Label(self, text=conf.units[i]+" / div ")
            ul.pack(side=LEFT)
            self.labels[i] = ul

        # create x-axis controls (starting from the right)
        ## x-axis units label
        ##  keep the spaces at the end of the label - os/x aqua ui draws that ugly resizeer triangle there (bottom right of the window)
        self.labels[conf.x_values] = Label(self, text=conf.units[conf.x_values]+" / div    ")
        self.labels[conf.x_values].pack(side=RIGHT)

        ## x-axis scaler
        sb = Spinbox(self, values=conf.values_upd[conf.x_values], from_=0, to=99999, width=5, command=partial(self.sb_handler, 0))
        sb.pack(side=RIGHT)
        self.scalers[conf.x_values] = sb
        sb.bind("<Button-4>", partial(self.sw_handler, conf.x_values))
        sb.bind("<Button-5>", partial(self.sw_handler, conf.x_values))
        sb.bind("<KeyRelease>", partial(self.sb_handler, conf.x_values))

        ## x-axis values chooser
        ### dictionary of possible values and their corresponding ox.values index
        vals = {}
        rvals = {}
        for i in range(min(ox.nvalues for ox in conf.open_experiments) + 1):  # loop i=0 (Time) to minimum nvalues of all open experiments + 1 
            desc = ""
            for vdesc in [ox.get_desc(i) for ox in conf.open_experiments]:
                if not desc.startswith(vdesc):
                    desc += " (%s)" % vdesc
            vals[vdesc] = i
            rvals[i] = vdesc                                    # the reverse dictionary to look up the default setting string

        ### set up an OptionMenu with a StringVar traced variable
        v = StringVar()                                         # create a StringVar and set its default value
        v.set(rvals[conf.x_values])                             # FIRST set()
        v.trace("w", partial(self.xv_handler, v))               # THEN  trace() - keep the order here!
        self.xchooser = OptionMenu(self, v, *vals.keys())
        self.xchooser.pack(side=RIGHT)
        self.xchooser.vals = vals                               # keep a reference to the dict created above

        # helps !
        #  to make make the xyplot canvas initially be resized properly
        #  -> reset_values_upd() setting proper scales -> xyplot bounding box matching canvas size/scroll region  
        self.window.tk.update_idletasks()

class ScrollRegion(Frame):
    "A Frame which can wrap another (child) widget and scroll it"

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
#        child_widget.bind("<Button-7>", self.xwheel_handler)    #  hmmm... I'm astonished that windows and mac handle mose scrollwheel events quiet
        child_widget.bind("<Button-1>", self.b1_handler)         # differently from linux. *me* of course thinks linux does it best, assigning additional buttons
        child_widget.bind("<Button1-Motion>", self.b1m_handler)  # To implement the scrollwheel handling on windows and mac would take too much time
        child_widget.bind("<ButtonRelease-1>", self.b1r_handler) # If you want to do it, have a look at the .delta event attribute, described here:
                                                                 # http://infohost.nmt.edu/tcc/help/pubs/tkinter/events.html#event-handlers

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
