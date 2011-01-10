# encoding: utf-8

from random import randint
from itertools import chain, count

from penview import *
from graph_view import XYPlot

# The application could be extended, such that an OpenExperiment could be
# displayed in more then one application window simultaneously, with different scales and colors.
# Therefore...
#  each PVWindow has ONE associated PVConf
#  each PVConf has A NUMBER OF associated OpenExperiments
#  each OpenExperiment has ONE associated ExperimentView PER PVConf that it is listed in
#  each ExperimentView has ONE associated PVWindow

class PVConf:
    """
    this is the central configuration data structure

    4 different types of listeners can be registered here:
    
    add_...(update):        update gets called on:
        ox_listener            opening/closing of experiments
        x_listener             change of x_values index
        scale_listener         change of scaling (values_upd)
        viewmode_listener      change of viewmode (table/graph)
    
    the update functions supplied should take exactly one argument, the conf object
    """

    def __init__(self):
        debug("debug is on")

        self.units = {}                 # the units of all data series - keys = index of a data series in the "values" matrix
                                        # len(units) is equal to the maximum number of data series of all currently open experiments + 1

        self.open_experiments = []      # list of OpenExperiment objects - the experiments currently opened
        self.ox_listeners = []

        self.x_values = 0               # index of the values currently used for the x-axis
        self.x_listeners = []

        self.values_upd = {}            # dict of scaling factors for all data series in "units per division"
        self.scale_listeners = []       # list of registered scale_listeners

        self.viewmode = ViewMode.graph  # current viewmode: graph or table
        self.viewmode_listeners = []

        self.recent_experiments = []    # list of RecentExperiment objects - maximum size 5, fifo semantics

        self.min_values = {}            # dict of minimum/maximum values of all data series,
        self.max_values = {}            #  THAT ARE VISIBLE in the window associated with this conf
                                        #  e.g. the _currently relevant_ extremes

    def add_open_experiment(self, ox):

        for i in range(ox.nvalues + 1):
            if i not in self.units:               # this experiments has more values than any other currently open experiment
                self.units[i] = ox.get_units(i)      # and therefore sets the standard now
            elif self.units[i] != ox.get_units(i):
                s = "s" if len(self.open_experiments) > 1 else ""
                raise Exception("This experiment can't be opened!\n\n" +
                                "The units are not matching those of the other already opened experiment%s." % s)

        self.open_experiments.append(ox)
        for update in self.ox_listeners: update(self)

    def _update_extremes(self, window):
        """
        find the extremes (minima and maxima) in all currently open experiments values, visible in the specified window
        e.g. the _currently relevant_ extremes
        """

        self.min_values = {}                                                # reset the min/max dicts
        self.max_values = {}

        def xupdate(i, min_, max_):                                         # helper function to update the self.min/max_values 
            if i not in self.min_values or min_ < self.min_values[i]:
                self.min_values[i] = min_
            if i not in self.max_values or max_ > self.max_values[i]:
                self.max_values[i] = max_

        for view in self.ox_views(window):                                  # for each ExperimentView associated with this window
            if not view.y_values:                                           # if there are no visible values
                continue                                                    # next - otherwise 

            maxlen = max(len(view.ox.values[i]) for i in view.y_values)     # maximum nr of elements of currently visible y-values
            min_ = min(view.ox.values[self.x_values][:maxlen])              # find the min/maximum x-value, USED by a currently visible y-value
            max_ = max(view.ox.values[self.x_values][:maxlen])
            xupdate(self.x_values, min_, max_)                              # update the extremes 

            for i in view.y_values:                                         # for all visible y- values
                xupdate(i, view.ox.min_values[i], view.ox.max_values[i])    # update the extremes using the precomputed min/max_values

    def set_x_values(self, index):
        old_x_values = self.x_values 
        self.x_values = index
        for view in chain(*(ox.views.values() for ox in self.open_experiments)):
            if index in view.y_values:
                view.remove_y_values(index)
        view.add_y_values(old_x_values)
        for update in self.x_listeners:
            update(self)

    def set_scale(self, n, scale):
        self.values_upd[n] = scale
        for update in self.scale_listeners:
            update(self)

    def set_viewmode(self, mode):
        self.viewmode = mode
        for update in self.viewmode_listeners:
            update(self)

    def add_ox_listener(self, update):
        self.ox_listeners.append(update)

    def add_x_listener(self, update):
        self.x_listeners.append(update)

    def add_scale_listener(self, update):
        self.scale_listeners.append(update)

    def add_viewmode_listener(self, update):	# table <> plot switch helper
        self.viewmode_listeners.append(update)

    # we should use properties more often, they're cool
    #
    def _get_nvalues(self):
        return len(self.units) - 1

    nvalues = property(fget=_get_nvalues)
    
    def ox_views(self, window):
        """return all experiment views for this window"""  
        return [ox.views[window] for ox in self.open_experiments if window in ox.views]

    def reset_scales(self, plot):
        "reset the scales to a sane default and notify all listeners afterwards"
        for i, scale in enumerate(self.default_scales(plot)):
            self.values_upd[i] = scale
        for update in self.scale_listeners:
            update(self)

    def default_scales(self, plot):
        """
        calculate scales such that all values fit into the given canvas size
        e.g. more or less the opposite of what bounding_box() does
        """

        # FIXME:
        #  in case the exactly same set of values are still plotted, this call is superfluous
        #  what should be done, really, would be to add a ExperimentView.listener for each experiment in this con
        #  and then make this call from that listener....
        self._update_extremes(plot.window)

        # the set of all y-values currently plotted for any experiment  
        y_values = reduce(lambda a,b:a|b, (view.y_values for view in self.ox_views(plot.window)))

        # the maximum value ranges in x- and y- direction
        xmaxrange = self.max_values[self.x_values] - self.min_values[self.x_values]
        ymaxrange = max(self.max_values[i] - self.min_values[i] for i in y_values)

        # FIXME:
        #  so far we use "method 1" all the time only
        #  we should do this properly before handing in our work
        #  otherwise somebody might one day realize that we bluffed a bit in our presentation... ;-)

        # FIXME:
        #  whatever the reason might be, that "- 4" is needed here: I'd love to know it, but for now...

        yield xmaxrange * plot.ppd / float(plot.winfo_width() - 4)
        for i in range(1, self.nvalues + 1):
            yield ymaxrange * plot.ppd / float(plot.winfo_height() - 4)

    def bounding_box(self, plot):
        """
        calculate the required canvas size to make all values fit into it with the current scales
        e.g. more or less the opposite of what default_scales() does
        """

        # the set of all y-values currently plotted for any experiment
        y_values = reduce(lambda a,b:a|b, (view.y_values for view in self.ox_views(plot.window)))
        
        # the left and right border of the bounding box in "divisions"
        xmin = self.min_values[self.x_values] / self.values_upd[self.x_values]
        xmax = self.max_values[self.x_values] / self.values_upd[self.x_values]

        # the lower and upper border of the bounding box in "divisions"
        ymin = min(self.min_values[i] / self.values_upd[i] for i in y_values)
        ymax = max(self.max_values[i] / self.values_upd[i] for i in y_values)

        # the bounding box in "pixels"
        return [int(v * plot.ppd) for v in (xmin, ymin, xmax, ymax)]

class OpenExperiment:
    """
    this structure holds the experiment data
    """

    # a counter to assign a unique id to each open experiment
    #
    ids = count()

    def __init__(self, ex_file, window):

        self.id = OpenExperiment.ids.next()

        self.file = ex_file
        self.views = { window: ExperimentView(self, window) }   # it could one day be possible to display an OpenExperiment
                                                                # simultaneously in different windows, in different colors, ...
                                                                # FIXME: only one view per window is possible right now

        vals = ex_file.load_values()                            # the experment data, organized in a "column-array"
        if vals[0][0] == None:                                  # if there are no time values
            self.time = False                                   # record that fact and
            self.values = [range(len(vals))]                    # fill in a continuous range of ints instead
            self.values += zip(*(r[1:] for r in vals))          # so the data can still be plotted against those
        else:
            self.time = True                                    # if the time values are there, it's simple
            self.values = zip(*vals)                            # just transpose the loaded values array

        self.metadata = ex_file.load_metadata()
        
        self.min_values = map(min, self.values)                 # static lists of extremes of each data series
        self.max_values = map(max, self.values)

    def get_additional_info(self):
        "return any additional info"
        additional_info = self.metadata['additional_info']
        return additional_info

    def get_actor_name(self):
        "return actor_name from metadata-table"
        actor_name = self.metadata['actor_name']
        return actor_name

    def get_date(self):
        "return date unformatted from metadata-table"
        date = self.metadata['date']
        return date
    
    def get_exp_name(self):
        "return the experiment name"
        exp_name = self.metadata['exp_name']
        return exp_name

    def get_desc(self, n):
        "return vn_desc"
        if n == 0:
            return "Zeit" if self.time else "Messung"
        return self.metadata['v' + str(n) + '_desc']

    def get_units(self, n):
        "return vn_unit"
        if n == 0:
            return "s" if self.time else "n"
        return self.metadata['v' + str(n) + '_unit']

    # simplified access to self.file.nvalues without copying it
    #
    nvalues = property(fget=lambda self: self.file.nvalues)

class ExperimentView:
    """
    one kind of listener can be registered:
    
    add_listener(update):  update gets called on change of visible data series or colors
    """
    def __init__(self, ox, window):

	self.ox = ox
        self.window = window

        self.listeners = []
        self.y_values = set(range(1, ox.nvalues + 1))           # list of indices of values visible on y-axis

        existing_colors = [[ v>>8 for v in window.tk.winfo_rgb(window.data_region.xy_plot.canvas_color) ]]
        for view in window.conf.ox_views(window):
            existing_colors += [[ v>>8 for v in window.tk.winfo_rgb(color) ] for color in view.colors ]

        self.colors = self.random_colors(ox.nvalues + 1, 128, existing_colors)

    @staticmethod
    def random_colors(ncolors, min_distance, existing=[]):
        """
        find a return a number (ncolors) of random colors
        having a minimum 'vectorial distance' of min_distance to each other as well as existing_colors
        """

        colors = []
        ntries = 3 * (ncolors + len(existing))

        get_one = lambda: \
            (randint(0, 255), randint(0, 255), randint(0, 255))

        # returns a positive (or zero) integer
        distance = lambda color1, color2: \
            sum(abs(component1 - component2) for component1, component2 in zip(color1, color2))

        for i in range(ncolors):
            # loop until...
            while True:
                # try 3 * (ncolors + len(existing)) times
                for j in range(ntries):
                    new = get_one()
                    # check if the distance from every other color exceeds the minimum distance
                    for old in colors + existing:
                        # if not, try again
                        if distance(new, old) < min_distance:
                            # set new = None, so in case this is the last of ntries tries at that min_distance
                            # the outer loop can detect the failure
                            new = None
                            break
                # ... a suitable new color is found
                if new:
                    break
                # this function never fails, so if a suitable color is
                # still not found, decrease min_distance (permanently, for the current function call)
                # eventually, this could decrease to zero, in which case distance() CAN'T be smaller any more
                min_distance /= 2
                debug("no suitable random color found after %d tries - decreased min_distance to %d" % (ntries, min_distance))
            colors.append(new)

        return ["#%02x%02x%02x" % c for c in colors]

    def add_listener(self, update):
        self.listeners.append(update)

    def set_color(self, i, color):
        self.colors[i] = color
        for update in self.listeners: update(self)

    def add_y_values(self, index):
        self.y_values.add(index)
        for update in self.listeners: update(self)

    def remove_y_values(self, index):
        self.y_values.remove(index)
        for update in self.listeners: update(self)

class RecentExperiment:
    def __init__(self):
        self.name = None
        self.path = None
