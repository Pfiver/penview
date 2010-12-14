from ttk import Notebook # ttk wrapper for TABS
from Tkinter import *
from penview_model import *


class TabRegion(Frame):
    def __init__(self, parent, pvconf):
        Frame.__init__(self, parent)
        self.tabs = []
        self.pvconf = pvconf
        self.pvconf.add_listener(self)
        self.notebook = Notebook(self)
        self.notebook.pack()
        
        self.pvconf.add_open_experiment(OpenExperiment('examples/abklingkonstante.sqlite'))
        self.pvconf.add_open_experiment(OpenExperiment('examples/abklingkonstante.sqlite'))

    def update(self):
        for a in self.pvconf.open_experiments:
            if a.id not in map(lambda t: t.id, self.tabs):
                self.addTab(a)
            
    def addTab(self, ox):
        tab = Label(text=ox.get_details_text())
        tab.id = ox.id
        self.tabs.append(tab)
        self.notebook.add(tab, text="Exp %d" % ox.id)