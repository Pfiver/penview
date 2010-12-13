#!/usr/bin/python
# encoding: utf-8

from data_access import ExperimentFile
    
class OpenExperiment:
    def __init__(self):
        self.experiment_perspective = None
        e = ExperimentFile('examples/abklingkonstante.sqlite',1)
        self.values = e.load_values(1)
        self.metadata = e.load_metadata()

    def get_actor_name(self):
        actor_name = self.metadata['actor_name']
        return actor_name

    def get_date(self):
        date = self.metadata['date']
        return date
    
    #TODO: in view auslagern!
    def get_details_text(self):
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
        return self.values
        
    def get_time_values(self):
        time_values = []
        for i in range(len(self.values)):
            time_values.append(self.values[i][0])
        return time_values
        
    def get_nvalues(self):
        """returns the number of values (v1, v2, v3, v4 -> 4) in table 'values' """
        nvalues = len(self.values[0])-1
        return nvalues
        
    def get_desc(self):
        desc = []
        for i in range(self.get_nvalues()):
            key = 'v' + str(i+1) + '_desc'
            #print "key: %s" % key
            desc.append(self.metadata[key])
        return desc

class ExperimentPerspective(object):
    def __init__(self):
        self.values_upd = None
        self.xaxis_values = None
        self.yaxis_values = None
        pass
    
class PenViewConf(object):
    def __init__(self):
        self.openExperiments = None
        self.recentExperiments = None
        pass

class RecentExperiment(object):
    def __init__(self):
        self.name = None
        self.path = None
        pass
    
a = OpenExperiment()
print a.values
print a.metadata
print a.get_details_text()
print a.get_time_values()
print a.get_nvalues()
print a.get_desc()