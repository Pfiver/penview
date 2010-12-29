# encoding: utf-8

from random import randint
from itertools import count

from penview import *

# The application could be extended, such that an OpenExperiment could be
# displayed in more then one application window simultaneously, with different scales and colors.
# Therefore...
#  each PVWindow has ONE associated PVConf
#  each PVConf has A NUMBER OF associated OpenExperiments
#  each OpenExperiment has ONE associated ExperimentView PER PVConf that it is listed in
#  each ExperimentView has ONE associated PVWindow

class PVConf:
    """
    4 different types of listeners can be registered:
    
    add_...(update):        update gets called on:
        ox_listener            opening/closing of experiments
        x_listener             change of x_values index
        scale_listener         change of scaling (values_upd)
        viewmode_listener      change of viewmode (table/graph)
    
    the update functions supplied should take exactly one argument, the conf object
    """
    def __init__(self):

        self.units = {}                 # the units of all data series - keys = index of a data series in the "values" matrix
                                        # len(units) is equal to the maximum number of data series of all currently open experiments

        self.open_experiments = []      # list of OpenExperiment objects - the experiments currently opened
        self.ox_listeners = []

        self.x_values = 0               # index of the values currently used for the x-axis
        self.x_listeners = []

        self.values_upd = {}            # dict of scaling factors for all values
        self.scale_listeners = []

        self.viewmode = ViewMode.graph  # current viewmode: graph or table
        self.viewmode_listeners = []

        self.recent_experiments = []    # list of RecentExperiment objects - maximum size 5, fifo semantics

    def add_open_experiment(self, ox):

        for i in range(ox.nvalues):
            if i not in self.units:               # this experiments has more values than any other currently open experiment
                self.units[i] = ox.get_units(i)      # and therefore sets the standard now
            elif self.units[i] != ox.get_units(i):
                s = len(self.open_experiments) > 1 and "s" or ""
                raise Exception("This experiment can't be opened!\n\n" +
                                "The units are not matching those of the other already opened experiment%s." % s)

        self.open_experiments.append(ox)

        for update in self.ox_listeners: update(self)

    # we should use properties more often, they're cool
    #
    def _get_nvalues(self):
        return len(self.units)

    nvalues = property(fget=_get_nvalues)

    def set_x_values(self, index):
        self.x_values = index
        for update in self.x_listeners: update(self)

    def set_scale(self, n, scale):
        self.values_upd[n] = scale
        for update in self.scale_listeners: update(self)

    def set_viewmode(self, mode):
        self.viewmode = mode
        for update in self.viewmode_listeners: update(self)

    def add_ox_listener(self, update):
        self.ox_listeners.append(update)

    def add_x_listener(self, update):
        self.x_listeners.append(update)

    def add_scale_listener(self, update):
        self.scale_listeners.append(update)

    def add_viewmode_listener(self, update):	# table <> plot switch helper
        self.viewmode_listeners.append(update)

    def reset_upd(self, ppd, width, height):	# FIXME FIXME FIXME: FIXME

        experiments = self.open_experiments

        cols = experiments[0].nvalues + 1

        min_values = []
        max_values = []
        for i in range(cols):
            imin = None
            imax = None
            for j in range(len(experiments)):
                jmin = min(experiments[j].values[i])
                jmax = max(experiments[j].values[i])
                if not imin or jmin < imin:
                    imin = jmin
                if not imax or jmax > imax:
                    imax = jmax
            min_values.insert(i, imin)
            max_values.insert(i, imax)

        maxranges = [max_values[i] - min_values[i] for i in range(cols)]

        xmaxrange = maxranges[0]
        ymaxrange = max(maxranges[1:])

        self.set_scale(0, ppd * xmaxrange / float(width))
        for i in range(1, cols):
            self.set_scale(i, ppd * ymaxrange / float(height))

        pxoff = - min_values[0] / xmaxrange * float(width)
        pyoff = - min(min_values[1:]) / ymaxrange * float(height)

        return (int(pxoff), int(pyoff))

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

        self.values = zip(*ex_file.load_values())
        self.metadata = ex_file.load_metadata()

    def get_additional_info(self):
        additional_info = self.metadata['additional_info']
        return additional_info

    def get_actor_name(self):
        """return actor_name from metadata-table"""
        actor_name = self.metadata['actor_name']
        return actor_name

    def get_date(self):
        """return date unformatted from metadata-table"""
        date = self.metadata['date']
        return date
    
    def get_exp_name(self):
        exp_name = self.metadata['exp_name']
        return exp_name

    def get_desc(self, n):
        """return vn_desc"""
        if n == 0:
            return "Zeit"
        key = 'v' + str(n) + '_desc'
        return self.metadata[key]

    def get_units(self, n):
        return self.metadata['v' + str(n+1) + '_unit']

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
        self.colors = self.random_colors(ox.nvalues + 1, 128)

    @classmethod
    def random_colors(cls, ncolors, min_distance):

        colors = []
        ntries = 3 * ncolors

        get_one = lambda: \
            (randint(0, 255), randint(0, 255), randint(0, 255))

        # returns a positive (or zero) integer
        distance = lambda color1, color2: \
            sum(abs(component1 - component2) for component1, component2 in zip(color1, color2))

        for i in range(ncolors):
            # loop until...
            while True:
                # try 3 * ncolors times
                for j in range(ntries):
                    new = get_one()
                    # check if the distance from every other color exceeds the minimum distance
                    for existing in colors:
                        # if not, try again
                        if distance(new, existing) < min_distance:
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
                debug("no suitable random color found after %d tries - decreasing min_distance" % ntries)
                min_distance /= 2
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
