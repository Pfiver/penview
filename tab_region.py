# encoding: utf-8
from ttk import Notebook # ttk wrapper for TABS
from Tkinter import *
from itertools import count
import tkColorChooser

from penview_model import *


class TabRegion(Frame):
    def __init__(self, parent, pvconf):
        Frame.__init__(self, parent)

        self.tabs = []
        self.colors = ["grey", "black", "red", "green", "blue", "cyan", "yellow", "magenta"]
        self.colors_id = count()
        pvconf.add_listener(self.update)

        self.notebook_region = Notebook(self)
        self.switch_region = Frame(self, bg="blue")

        self.button1 = Button(self.switch_region, text="Graph", command='', relief=SUNKEN)
        self.button2 = Button(self.switch_region, text="Table", command='')
        self.button1.pack(side=LEFT)
        self.button2.pack(side=LEFT)

        self.notebook_region.pack(fill=BOTH, expand=1)
        self.switch_region.pack(fill=X, side=BOTTOM)
        
#        self.e = 'examples/abklingkonstante.sqlite'
#        pvconf.add_open_experiment(OpenExperiment(self.e))
#        pvconf.add_open_experiment(OpenExperiment(self.e))
#        pvconf.add_open_experiment(OpenExperiment(self.e))

    def update(self, conf):
        for a in conf.open_experiments:
            if a.id not in map(lambda t: t.id, self.tabs):
                self.addTab(a)
    
    def choose_color(self, color):
#        color_id = self.colors_id.next()
        color = self.colors[0]
        tkColorChooser.askcolor(color)
        
    def addTab(self, ox):
        tab = Frame(self)
        tab.grid()
        Checkbutton(tab, text="Zeit").grid(row=0, sticky=W)
        for y in range(ox.get_nvalues()):
            checkb = Checkbutton(tab, text=ox.get_desc()[y])
            checkb.grid(row=1, column=0, sticky=W)
            color_id = self.colors_id.next()
            color = self.colors[color_id]
            colorb = Button(tab, bg=color, command=self.choose_color)
            colorb.grid(row=1, column=1, sticky=E)
            
        Label(tab, text=self.get_details_text(ox)).grid(row=2, sticky=W)
        tab.id = ox.id
        self.tabs.append(tab)
        self.notebook_region.add(tab, text="Exp %d" % ox.id)
        
    def get_details_text(self, ox):
        """return actor_name, date and ev. additional_details from OpenExperiment"""
        #Durchgeführt von: Namen
        actor_name = ox.get_actor_name()
        details_text =  "Durchgeführt von %s" % actor_name
        #Datum
        date = ox.get_date()
        YYYY = date[0:4]
        MM = date[4:6]
        DD = date[6:8]
#        print "YYYYMMDD: %s.%s.%s" % ( DD, MM, YYYY )
        details_text += "\nDatum, %s.%s.%s" % ( DD, MM, YYYY )
        try:
            #Konstante (z.b. Federkonstante)
            additional_info = ox.get_additional_info()
            details_text += "\n%s" % additional_info
        except:
            pass
        return details_text
        
        # import tkColorChooser
        # tkColorChooser.askcolor()
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/dialogs.html#tkColorChooser