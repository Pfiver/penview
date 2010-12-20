#!/usr/bin/python
# encoding: utf-8

from itertools import count

from penview import *
from data_access import ExperimentFile
from data_region import XYPlot, PVTable

class PenViewConf:
    ox_ids = count()
    def __init__(self):

        # 3 different types of listeners can be registered:
        #
        # add_...          get notified on ...
        # ox_listener:     opening/closing of experiments
        # view_listener:   view change (table/graph)
        # scale_listener:  change of scaling (values_upd)
        #
        # the update functions supplied should take exactly one argument, the conf object

        self.open_experiments = []    # list of OpenExperiment objects - the experiments currently opened
        self.ox_listeners = []

        self.view = XYPlot            # either XYPlot or PVTable (a class object)
        self.view_listeners = []

        self.values_upd = {}          # dict of scaling factors for values
        self.scale_listeners = []

        self.recent_experiments = []  # list of RecentExperiment objects - maximum size 5, fifo semantics

    def add_open_experiment(self, ox):
        ox.id = PenViewConf.ox_ids.next()
        self.open_experiments.append(ox)

        self.controller.reset_upd()             # initialize scale to a sane default (all data visible)

        for update in self.ox_listeners: update(self)

    def set_view(self, view):
        self.view = view
        for update in self.view_listeners: update(self)

    def set_scale(self, n, scale):
        self.values_upd[n] = scale
        for update in self.scale_listeners: update(self)

    def add_ox_listener(self, update):
        self.ox_listeners.append(update)

    def add_view_listener(self, update):     # table <> plot switch helper
        self.view_listeners.append(update)

    def add_scale_listener(self, update):
        self.scale_listeners.append(update)

    def set_controller(self, controller):
        self.controller = controller

class OpenExperiment:
    def __init__(self, ex_file):
        """
        initialize Experiment: load values and metadata table into classvariables
             :Parameters:
                path  file-path
        """
        self.file = ex_file
        self.perspective = ExperimentPerspective(0, [i+1 for i in range(self.get_nvalues())])

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
    
    def get_nvalues(self):
        return self.file.nvalues

    def get_desc(self, n):
        """return vn_desc"""
        key = 'v' + str(n) + '_desc'
        return self.metadata[key]

class ExperimentPerspective:
    def __init__(self, xvals, yvals):

        # one listener can be registered:
        #
        # add_...          get notified on ...
        # values_listener: change of visible data series

        self.xaxis_values = xvals  # index of current xaxis values
        self.yaxis_values = yvals  # list of indices of values visible on yaxis
        self.values_listeners = []
        
    def add_values_listener(self, update):
        self.values_listeners.append(update)

    def set_xaxis(self, index):
        self.xaxis_values = index
        for update in self.values_listeners: update(self)

    def set_yaxis(self, indices):
        self.yaxis_values = indices
        for update in self.values_listeners: update(self)

class RecentExperiment:
    def __init__(self):
        self.name = None
        self.path = None

