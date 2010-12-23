# encoding: utf-8
from Tkinter import *
from itertools import count
import tkColorChooser

from penview_model import *
from data_region import XYPlot, PVTable

from ttk import Notebook # ttk wrapper for TABS

class TabRegion(Frame):
    def __init__(self, parent, pvconf, ctrl):
        Frame.__init__(self, parent)

        self.tabs = []
        self.colors = ["grey", "black", "red", "green", "blue", "cyan", "yellow", "magenta"]
        self.colors_id = count()

        pvconf.add_ox_listener(self.ox_update)

        # Tabs in notebook_region
        self.notebook_region = Notebook(self)
        
        # Graph and Table Buttons in switch_region
        self.switch_region = Frame(self)
        self.graph_button = Button(self.switch_region, text="Graph", command=lambda: ctrl.q(PVAction.show_graph))
        self.table_button = Button(self.switch_region, text="Table", command=lambda: ctrl.q(PVAction.show_table))
        self.graph_button.pack(side=LEFT, fill=X, expand=YES)
        self.table_button.pack(side=LEFT, fill=X, expand=YES)
        pvconf.add_view_listener(self.view_update)

        # pack()
        self.notebook_region.pack(fill=BOTH, expand=1)
        self.switch_region.pack(fill=X, side=BOTTOM)

    def ox_update(self, conf):
        for a in conf.open_experiments:
            if a.id not in map(lambda t: t.id, self.tabs):
                self.addTab(a)

    def view_update(self, conf):
        view_buttons = { XYPlot: self.graph_button,
                         PVTable: self.table_button }
        for v in view_buttons:
            if conf.view == v:
                view_buttons[v].config(relief=SUNKEN)
            else:
                view_buttons[v].config(relief=RAISED)

    def choose_color(self):
#        color_id = self.colors_id.next()
        color = self.colors[0]
        tkColorChooser.askcolor()
        
    def addTab(self, ox):
        tab = Frame(self)
        Checkbutton(tab, text="Zeit").grid(row=0, sticky=W)

        checkb = Checkbutton(tab, text="Zeit")
        checkb.grid(row=0, column=0, sticky=W)

        for i in range(ox.get_nvalues()):
            checkb = Checkbutton(tab, text=ox.get_desc(i))
            checkb.grid(row=1, column=0, sticky=W)
            color_id = self.colors_id.next()
            color = self.colors[color_id]
            colorb = Button(tab, bg=color, width=1, height=1, command=self.choose_color)
            colorb.grid(row=i+1, column=1, sticky=E)

        Label(tab, text=self.get_details_text(ox)).grid(row=2, sticky=W, columnspan=2)
        tab.id = ox.id
        tab.pack()
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
