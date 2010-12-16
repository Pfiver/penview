from Tkinter import *

from penview import *
from data_import import *
from penview_model import *

class OpenWizard:
    
    @classmethod
    def get_path(cls):
        debug()
        return "examples/abklingkonstante.sqlite"
    
    @classmethod
    def open_experiment(cls):
        return OpenExperiment(ExperimentFile(cls.get_path()))

class ImportWizard:
    
    @classmethod
    def get_csv_path(cls):
        debug()
        return "examples/Abklingkonstante.csv"
    
    @classmethod
    def get_experiment_path(cls):
        return "examples/abklingkonstante.sqlite"
    
    @classmethod
    def open_experiment(cls):
        csv = CSVImporter(cls.get_csv_path())
        ex_file = ExperimentFile(cls.get_experiment_path(), len(csv.values) - 1)
        
        ex_file.store_values(1, csv.values)
        ex_file.store_metadata(csv.metadata)
        
        return OpenExperiment(ex_file)
