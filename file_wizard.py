from Tkinter import *
from tkFileDialog import *
from itertools import count

from penview import *
from data_import import *
from penview_model import *

class OpenWizard:

    xi = count()
    examples = ('examples/abklingkonstante.sqlite',
                'examples/eigenfrequenz_chaos2.sqlite',
#                'examples/motorkalibrierung.sqlite',
    )

    @classmethod
    def get_path(cls):
        if debug_flag:
            return cls.examples[cls.xi.next()]

        return askopenfilename(filetypes=(("Experiment Files", "*.sqlite"),))
    
    @classmethod
    def open_experiment(cls):
        return OpenExperiment(ExperimentFile(cls.get_path()))

class ImportWizard:

    xi = count()
    examples = 'examples/Abklingkonstante.csv'

    @classmethod
    def get_csv_path(cls):
        if debug_flag:
            return cls.examples[cls.xi.next()]

        return askopenfilename(filetypes=(("CSV Files", "*.csv"),))
    
    @classmethod
    def get_experiment_path(cls):
        if debug_flag:
            return cls.examples[cls.xi] + ".imported.sqlite"

        return asksaveasfilename(filetypes=(("Experiment Files", "*.sqlite"),))
    
    @classmethod
    def open_experiment(cls):
        csv = CSVImporter(cls.get_csv_path())
        ex_file = ExperimentFile(cls.get_experiment_path(), csv.rowsize-1)
        
        ex_file.store_values(1, csv.values)
        ex_file.store_metadata(csv.metadata)
        
        return OpenExperiment(ex_file)
