from Tkinter import *
from tkFileDialog import *

from penview import *
from data_import import *
from penview_model import *

class OpenWizard:
    
    @classmethod
    def get_path(cls):
        if debug_flag:
            return "examples/abklingkonstante.sqlite"
        return askopenfilename(filetypes=(("Experiment Files", "*.sqlite"),))
    
    @classmethod
    def open_experiment(cls):
        return OpenExperiment(ExperimentFile(cls.get_path()))

class ImportWizard:
    
    @classmethod
    def get_csv_path(cls):
        if debug_flag:
            return "examples/Abklingkonstante.csv"
        return askopenfilename(filetypes=(("CSV Files", "*.csv"),))
    
    @classmethod
    def get_experiment_path(cls):
        if debug_flag:
            return "examples/abklingkonstante_imported.sqlite"
        return asksaveasfilename(filetypes=(("Experiment Files", "*.sqlite"),))
    
    @classmethod
    def open_experiment(cls):
        csv = CSVImporter(cls.get_csv_path())
        ex_file = ExperimentFile(cls.get_experiment_path(), csv.rowsize-1)
        
        ex_file.store_values(1, csv.values)
        ex_file.store_metadata(csv.metadata)
        
        return OpenExperiment(ex_file)
