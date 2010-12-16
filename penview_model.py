#!/usr/bin/python
# encoding: utf-8

from itertools import count

from penview import *
from data_access import ExperimentFile
    
class OpenExperiment:
    def __init__(self, path, nvalues):
        """initialize Experiment: load values and metadata table into classvariables
                  :Parameters:
            path  file-path"""
        self.experiment_perspective = None
        e = ExperimentFile(path, nvalues)
        if nvalues != self.get_nvalues():
            #TODO solve this
            raise Exception("Circular Dependencies..")
        self.values = e.load_values()
        self.metadata = e.load_metadata()
        print "%s values: %s " % ( path, self.values )
        print "%s meta: %s" % ( path, self.metadata )
    
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
        
    def get_values(self):
        """return a list of all values from values-table"""
        return self.values
        
    def get_time_values(self):
        """return list of time values from values-table"""
        time_values = []
        for i in range(len(self.values)):
            time_values.append(self.values[i][0])
        return time_values
        
#    def get_nvalues(self):
#        """return the number of values (v1, v2, v3, v4 -> 4) in table 'values' """
#        debug("self.values[0]: " + str(self.values[0]))
#        nvalues = len(self.values[0])
#        return nvalues
    
    def get_nvalues(self):
        row = self.values[1]
        rowsize = -1
        if rowsize == -1:
            rowsize = len(row)
            for value in reversed(row): # test how big the row is and ignore further values
                if value == '':
                    rowsize -= 1
                else:
                    break
        nvalues = rowsize
        return nvalues
    
        
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
    def __init__(self):
        """ Initialize Perspective
        """
        self.values_upd = [] # list of scaling factor for ALL values 
        self.xaxis_values = 0 # index of current xaxis values
        self.yaxis_values = [] # list of indices of values visible on yaxis

class RecentExperiment:
    def __init__(self):
        self.name = None
        self.path = None

class PenViewConf:
    ox_ids = count()
    def __init__(self):
        self.listeners = []         # list of listener functions taking one argument: the conf that was updated
        self.open_experiments = []      # list of OpenExperiment objects - the experiments currently opened  
        self.recent_experiments = []        # list of RecentExperiment objects - maximum size 5, fifo semantics    

    def add_open_experiment(self, ox):
        ox.id = PenViewConf.ox_ids.next()
        self.open_experiments.append(ox)
        for update in self.listeners:
            update(self)

    def add_listener(self, listener):
        self.listeners.append(listener)

    def set_controller(self, controller):
        self.controller = controller
    
#a = OpenExperiment('examples/abklingkonstante.sqlite')
#a = OpenExperiment('examples/motorkalibrierung.sqlite')
#print a.values
#print a.metadata
#print a.get_time_values()
#print a.get_nvalues()
#print a.get_desc()
