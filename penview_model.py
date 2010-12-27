# encoding: utf-8

from random import randint
from itertools import count

from penview import *
from data_access import ExperimentFile
from data_region import XYPlot, PVTable

class PenViewConf:

    def __init__(self):

        self.units = {}              # you can always count on 
                                     # len(units) == the number of values of the currently open experiment that has the most values

        # 3 different types of listeners can be registered:
        #
        # add_...              get notified on ...
        # ox_listener:         opening/closing of experiments
        # scale_listener:      change of scaling (values_upd)
        # viewmode_listener:   view change (table/graph)
        #
        # the update functions supplied should take exactly one argument, the conf object

        self.open_experiments = []    # list of OpenExperiment objects - the experiments currently opened
        self.ox_listeners = []

        self.values_upd = {}          # dict of scaling factors for values
        self.scale_listeners = []

        self.viewmode = XYPlot        # either XYPlot or PVTable (a class object)
        self.viewmode_listeners = []

        self.recent_experiments = []  # list of RecentExperiment objects - maximum size 5, fifo semantics

    def add_open_experiment(self, ox):

        for i in range(ox.get_nvalues()):
            if i not in self.units:               # this experiments has more values than any other currently open experiment
                self.units[i] = ox.get_units(i)      # and therefore sets the standard now
            elif self.units[i] != ox.get_units(i):
                raise Exception("can't open this experiment - units not matching those of of already open experiments")

        self.open_experiments.append(ox)

        for update in self.ox_listeners: update(self)

    def _get_nvalues(self):
        return len(self.units)

    nvalues = property(fget=_get_nvalues)        # as seen here: http://arkanis.de/weblog/2010-12-19-are-getters-and-setters-object-oriented#comment-2010-12-19-23-58-06-chris-w

    def set_scale(self, n, scale):
        self.values_upd[n] = scale
        for update in self.scale_listeners: update(self)

    def set_viewmode(self, mode):
        self.viewmode = mode
        for update in self.viewmode_listeners: update(self)

    def add_ox_listener(self, update):
        self.ox_listeners.append(update)

    def add_scale_listener(self, update):
        self.scale_listeners.append(update)

    def add_viewmode_listener(self, update):     # table <> plot switch helper
        self.viewmode_listeners.append(update)

    def set_controller(self, controller):
        self.controller = controller

    def reset_upd(self, ppd, width, height):

        experiments = self.open_experiments

        cols = experiments[0].get_nvalues() + 1

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

        debug("min: " + str(min_values))
        debug("max: " + str(max_values))

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
    ids = count()

    def __init__(self, ex_file, ui):
        """
        initialize Experiment: load values and metadata table into classvariables
             :Parameters:
                path  file-path
        """

        self.id = OpenExperiment.ids.next()

        self.file = ex_file
        self.view = ExperimentView(self, ui)

        self.values = zip(*ex_file.load_values())
        self.sqlvalues = ex_file.load_values()
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
    
    def get_nvalues(self):
        return self.file.nvalues

    def get_desc(self, n):
        """return vn_desc"""
        if n == 0:
            return "Zeit"
        key = 'v' + str(n) + '_desc'
        return self.metadata[key]

    def get_units(self, n):
        return self.metadata['v' + str(n+1) + '_unit']

class ExperimentView:
    def __init__(self, ox, ui):

        # one listener can be registered:
        #
        # add_...          get notified on ...
        # values_listener: change of visible data series or their colors

        self.experiment = ox
        self.listeners = []
        self.x_values = 0                               # index of current xaxis values
        self.y_values = range(1, ox.get_nvalues() + 1)  # list of indices of values visible on yaxis
        self.colors = self.random_colors(ox.get_nvalues() + 1, 128)

    @classmethod
    def random_colors(cls, ncolors, min_distance):

        colors = []

        get_one = lambda: \
            (randint(0, 255), randint(0, 255), randint(0, 255))

        # returns a positive (or zero) integer
        distance = lambda color1, color2: \
            sum(abs(component1 - component2) for component1, component2 in zip(color1, color2))

        for i in range(ncolors):
            # loop until...
            while True:
                # try 3 * ncolors times
                for j in range(3 * ncolors):
                    new = get_one()
                    # check if the distance from every other color exceeds the minimum distance
                    for existing in colors:
                        # if not, try again
                        if distance(new, existing) < min_distance:
                            # set new = None, so in case this is the last of (3 * ncolors) tries at that min_distance
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
            colors.append(new)

        return ["#%02x%02x%02x" % c for c in colors]

    def add_listener(self, update):
        self.listeners.append(update)

    def set_xaxis(self, index):
        self.x_values = index
        for update in self.listeners: update(self.experiment)

    def set_yaxis(self, indices):
        self.y_values = indices
        for update in self.listeners: update(self.experiment)

    def set_color(self, i, color):
        self.colors[i] = color
        for update in self.listeners: update(self.experiment)

class RecentExperiment:
    def __init__(self):
        self.name = None
        self.path = None

