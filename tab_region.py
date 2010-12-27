# encoding: utf-8

from Tkinter import *
from itertools import count
from functools import partial
from tkColorChooser import askcolor

from penview_model import *
from data_region import XYPlot, PVTable

from ttk import Notebook # ttk wrapper for TABS

class TabRegion(Frame):
    def __init__(self, parent, pvconf, ctrl, **kwargs):
        Frame.__init__(self, parent, **kwargs)

        self.tabs = {}
        self.conf = pvconf

        pvconf.add_ox_listener(self.ox_update)

        # Tabs in notebook_region
        self.notebook_region = Notebook(self, width=350)
        
        # Graph and Table Buttons in switch_region
        self.switch_region = Frame(self)
        self.graph_button = Button(self.switch_region, text="Graph", command=lambda: ctrl.q(PVAction.show_graph))
        self.table_button = Button(self.switch_region, text="Table", command=lambda: ctrl.q(PVAction.show_table))
        self.graph_button.pack(side=LEFT, fill=X, expand=YES)
        self.table_button.pack(side=LEFT, fill=X, expand=YES)
        pvconf.add_viewmode_listener(self.viewmode_update)

        # pack()
        self.notebook_region.pack(fill=BOTH, expand=1)
        self.switch_region.pack(fill=X, side=BOTTOM)

        # keep a reference to some empty BitmapImage
        # ehr well .. this is needed because if you write Button(image=BitmapImage(), ...)
        # the BitmapImage object will be reaped by the garbage collector and the button doesn't work
        self.bi = BitmapImage()

    def ox_update(self, conf):
        for ox in conf.open_experiments:
            if ox.id not in self.tabs:
                self.addTab(ox)
                ox.view.add_listener(self.experiment_view_update)

    def viewmode_update(self, conf):
        view_buttons = { XYPlot: self.graph_button,
                         PVTable: self.table_button }
        for v in view_buttons:
            if conf.viewmode == v:
                view_buttons[v].config(relief=SUNKEN)
            else:
                view_buttons[v].config(relief=RAISED)

    def experiment_view_update(self, ox):
        tab = self.tabs[ox.id]
        for i in range(ox.get_nvalues() + 1):
#            tab.valueboxes[i]....
            tab.colorbuttons[i].config(bg=ox.view.colors[i], activebackground=ox.view.colors[i])

    def choose_color(self, view, i):
        view.set_color(i, askcolor()[1])
        
    def addTab(self, ox):
        tab = Frame(self)
        tab.valueboxes = {}
        tab.colorbuttons = {}

        for i in range(ox.get_nvalues() + 1):
            box = Checkbutton(tab, text=ox.get_desc(i))
            box.grid(row=i, column=0, sticky=W)
            tab.valueboxes[i] = box
            # creating a button with image=... lets you specify with and height in pixels
            button = Button(tab, image=self.bi, width=10, height=10,
                            bg=ox.view.colors[i], activebackground=ox.view.colors[i], command=partial(self.choose_color, ox.view, i))
            button.grid(row=i, column=1, padx=4, pady=4)
            tab.colorbuttons[i] = button

        Label(tab, text=self.get_details_text(ox), justify=LEFT).grid(columnspan=2, sticky=W)
        tab.grid_columnconfigure(0, weight=1)
        tab.pack()
        self.tabs[ox.id] = tab

        self.notebook_region.add(tab, text="Exp %d" % ox.id)

    @classmethod 
    def get_details_text(cls, ox):
        """return actor_name, date and ev. additional_details from OpenExperiment"""

        # Datum
        date = ox.get_date()
        YYYY = date[0:4]
        MM = date[4:6]
        DD = date[6:8]
        text = "Datum: %s.%s.%s" % ( DD, MM, YYYY )
        text += "\n"

        # Gruppe: Namen
        actor_name = ox.get_actor_name()
        text += "Gruppe: %s" % actor_name
        text += "\n"

        try:
            # Zusätzliche Informationen (z.b. Federkonstante)
            text += ox.get_additional_info()
            text += "\n"
        except:
            pass

        return text
        
        # import tkColorChooser
        # tkColorChooser.askcolor()
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/dialogs.html#tkColorChooser
