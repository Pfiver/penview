from ttk import Notebook # ttk wrapper for TABS
from Tkinter import *
from penview_model import *


class TabRegion(Frame):
    def __init__(self, parent, pvconf):
        Frame.__init__(self, parent)

        self.tabs = []
        pvconf.add_listener(self.update)

        self.notebook_region = Notebook(self)
        self.switch_region = Frame(self, bg="blue")

        self.button1 = Button(self.switch_region, text="Graph", command='', relief=SUNKEN)
        self.button2 = Button(self.switch_region, text="Table", command='')
        self.button1.pack(side=LEFT)
        self.button2.pack(side=LEFT)

        self.notebook_region.pack(fill=BOTH, expand=1)
        self.switch_region.pack(fill=X, side=BOTTOM)
        
        e = 'examples/abklingkonstante.sqlite'
        pvconf.add_open_experiment(OpenExperiment(e))
        pvconf.add_open_experiment(OpenExperiment(e))

    def update(self, conf):
        for a in conf.open_experiments:
            if a.id not in map(lambda t: t.id, self.tabs):
                self.addTab(a)
            
    def addTab(self, ox):
        tab = Label(text=ox.get_details_text())
        tab.id = ox.id
        self.tabs.append(tab)
        self.notebook_region.add(tab, text="Exp %d" % ox.id)
        
        # import tkColorChooser
        # tkColorChooser.askcolor()
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/dialogs.html#tkColorChooser