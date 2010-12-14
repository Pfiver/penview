#!/usr/bin/python
# encoding: utf-8

from data_access import ExperimentFile
    
class OpenExperiment:
    def __init__(self,nr):
        """initialize Experiment: load values and metadata table into classvariables
                  :Parameters:
            nr    data-set number"""
        self.experiment_perspective = None
        e = ExperimentFile('examples/abklingkonstante.sqlite',nr)
        self.values = e.load_values(nr)
        self.metadata = e.load_metadata()

    def get_actor_name(self):
        """return actor_name from metadata-table"""
        actor_name = self.metadata['actor_name']
        return actor_name

    def get_date(self):
        """return date unformatted from metadata-table"""
        date = self.metadata['date']
        return date
    
    #TODO: in view auslagern!
    def get_details_text(self):
        """return actor_name, date and ev. additional_details from metadata-table"""
        #Durchgeführt von: Namen
        actor_name = self.get_actor_name()
        details_text =  "Durchgeführt von %s" % actor_name
        #Datum
        date = self.get_date()
        details_text += "\nDatum, %s" % date
        try:
            #Konstante (z.b. Federkonstante)
            additional_info = self.metadata['additional_info']
            details_text += "\n%s" % additional_info
        except:
            pass
        return details_text
        
    def get_values(self):
        """return a list of all values from values-table"""
        return self.values
        
    def get_time_values(self):
        """return list of time values from values-table"""
        time_values = []
        for i in range(len(self.values)):
            time_values.append(self.values[i][0])
        return time_values
        
    def get_nvalues(self):
        """return the number of values (v1, v2, v3, v4 -> 4) in table 'values' """
        nvalues = len(self.values[0])-1
        return nvalues
        
    def get_desc(self):
        """return a list of vn_desc (v1, v2..)"""
        desc = []
        for i in range(self.get_nvalues()):
            key = 'v' + str(i+1) + '_desc'
            #print "key: %s" % key
            desc.append(self.metadata[key])
        return desc

class ExperimentPerspective:
    def __init__(self):
        """ Initialize Perspective
        
        """
        self.values_upd = [] # list of scaling factor for ALL values 
        self.xaxis_values = 0 # index of current xaxis values
        self.yaxis_values = [] # list of indices of values visible on yaxis
    
class PenViewConf:
    def __init__(self):
        self.openExperiments = None
        self.recentExperiments = None

class RecentExperiment:
    def __init__(self):
        self.name = None
        self.path = None
    
a = OpenExperiment(1)
#print a.values
#print a.metadata
#print a.get_details_text()
#print a.get_time_values()
#print a.get_nvalues()
#print a.get_desc()
