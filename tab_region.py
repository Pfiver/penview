from ttk import Notebook # ttk wrapper for TABS
from Tkinter import *
from penview_model import *


class TabRegion(Frame):
    def __init__(self, parent, pvconf):
        Frame.__init__(self, parent)
        self.tabs = []
        # self.pvconf = pvconf
        pvconf.add_listener(self.update)
        self.frame1 = Frame(self)
        self.frame2 = Frame(self.frame1)
        self.notebook_region = Notebook(self.frame2)
        self.frame3 = Frame(self.frame1)
        self.button1 = Button(self.frame3, text="Graph", command='', relief=SUNKEN)
        self.button2 = Button(self.frame3, text="Table", command='')
        
        self.button2.pack(side=LEFT)
        self.button1.pack(side=RIGHT)
        self.notebook_region.pack()
        self.frame3.pack(side='bottom')
        self.frame2.pack()
        self.frame1.pack()
        
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