from ttk import Notebook # ttk wrapper for TABS
from Tkinter import *
from penview_model import *


class TabRegion(Frame):
    def __init__(self, parent, pvconf):
        Frame.__init__(self, parent)
        self.tabs = []
        pvconf.add_listener(self)
        self.notebook = Notebook(self)
        self.notebook.pack()
        
        self.notebook.add(Label(text="TabRegion"),text="Tab1")
        
        a = OpenExperiment(1)
        print a.values
        print a.metadata
        print a.get_details_text()
        print a.get_time_values()
        print a.get_nvalues()
        print a.get_desc()

    def update(self):
        for x in pvconf.open_experiments:
            if x not in self.tabs:
                addTab(x)
            
    def addTab(self, file):
        