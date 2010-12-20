#!/usr/bin/python
# encoding: utf-8

from itertools import count

from penview import *
from data_access import ExperimentFile
from data_region import XYPlot, PVTable
    
class OpenExperiment:
    def __init__(self, ex_file):
        """
        initialize Experiment: load values and metadata table into classvariables
             :Parameters:
                path  file-path
        """
        self.file = ex_file
        self.perspective = ExperimentPerspective(0, [i+1 for i in range(ex_file.nvalues)])

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

#    def get_nvalues(self):
#        """return the number of values (v1, v2, v3, v4 -> 4) in table 'values' """
#        debug("self.values[0]: " + str(self.values[0]))
#        nvalues = len(self.values[0])
#        return nvalues
    
    def get_nvalues(self):
        
        return self.file.nvalues

#        row = self.values[1]
#        rowsize = -1
#        if rowsize == -1:
#            rowsize = len(row)
#            for value in reversed(row): # test how big the row is and ignore further values
#                if value == '':
#                    rowsize -= 1
#                else:
#                    break
#        nvalues = rowsize
#        return nvalues
    
        
    def get_desc(self):
        """return a list of vn_desc (v1, v2..)"""
        desc = []
        debug("nvalues: %s " % self.get_nvalues())
        for i in range(1, self.get_nvalues()):
            key = 'v' + str(i) + '_desc'
            value = self.metadata[key]
            debug("key:value %s:%s" % ( key, value ))
            desc.append(value)
        return desc

class ExperimentPerspective:
    def __init__(self, xvals, yvals):
        """ Initialize Perspective
        """
        self.xaxis_values = xvals  # index of current xaxis values
        self.yaxis_values = yvals # list of indices of values visible on yaxis

class RecentExperiment:
    def __init__(self):
        self.name = None
        self.path = None

class PenViewConf:
    ox_ids = count()
    def __init__(self):
        self.open_experiments = []    # list of OpenExperiment objects - the experiments currently opened
        self.ox_listeners = []        # list of listener functions getting called on add_open_experiment
                                      # the function should take exactly one argument: the conf that was updated

        self.recent_experiments = []  # list of RecentExperiment objects - maximum size 5, fifo semantics

        self.view = XYPlot            # either XYPlot or PVTable (a class object)
        self.view_listeners = []      # analog to ox_listeners

        self.values_upd = []          # list of scaling factor for ALL values

    def set_view(self, view):
        self.view = view
        for update in self.view_listeners:
            update(self)

    def add_view_listener(self, view_listener):
        self.view_listeners.append(view_listener)

    def add_open_experiment(self, ox):
        ox.id = PenViewConf.ox_ids.next()
        self.open_experiments.append(ox)
        for update in self.ox_listeners:
            update(self)

    def add_ox_listener(self, ox_listener):
        self.ox_listeners.append(ox_listener)

    def set_controller(self, controller):
        self.controller = controller
    
#a = OpenExperiment('examples/abklingkonstante.sqlite')
#a = OpenExperiment('examples/motorkalibrierung.sqlite')
#print a.values
#print a.metadata
#print a.get_time_values()
#print a.get_nvalues()
#print a.get_desc()
