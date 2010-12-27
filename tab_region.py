# encoding: utf-8

from Tkinter import *
from itertools import count
from threading import Event
from functools import partial
from tkColorChooser import askcolor

from penview_model import *
from data_region import XYPlot, PVTable

from ttk import Notebook # ttk wrapper for TABS

class TabRegion(Frame):
    def __init__(self, parent, view):
        Frame.__init__(self, parent)

        self.mapped = Event()           # are we packed ?

        self.tabs = {}
        self.view = view

        if not isinstance(parent, PanedWindow):
            raise InternalError("parent must be a PanedWindow")
        self.parent = parent    # parent is a PanedWindow

        view.conf.add_ox_listener(self.ox_update)

        # Tabs in notebook_region
        self.notebook_region = Notebook(self)
        
        # Graph and Table Buttons in switch_region
        self.switch_region = Frame(self)
        self.graph_button = Button(self.switch_region, text="Graph", command=lambda: view.controller.q(PVAction.show_graph))
        self.table_button = Button(self.switch_region, text="Table", command=lambda: view.controller.q(PVAction.show_table))
        self.graph_button.pack(side=LEFT, fill=X, expand=YES)
        self.table_button.pack(side=LEFT, fill=X, expand=YES)
        view.conf.add_viewmode_listener(self.viewmode_update)

        # pack()
        self.notebook_region.pack(fill=BOTH, expand=1)
        self.switch_region.pack(fill=X, side=BOTTOM)

        # once all gui elements are mapped, record that fact
        self.view.after_idle(self.mapped.set)                # at this point, view.tk is known to be instantiated

        # keep a reference to some empty BitmapImage
        # ehr well .. this is needed because if you write Button(image=BitmapImage(), ...)
        # the BitmapImage object will be reaped by the garbage collector and the button doesn't work
        self.bi = BitmapImage()

    def ox_update(self, conf):
        # clear the mapped Event (used by config_handler())
        # as we are going to add and resize some elements now
        self.mapped.clear()
        
        for ox in conf.open_experiments:
            if ox not in self.tabs:
                self.add_tab(ox)
                ox.view.add_listener(self.experiment_view_update)

        # re-add ourselves to the parent PanedWindow Widget
        # this will resize the tab_region to make all elements all tabs fit
        self.parent.remove(self)
        self.parent.add(self, before=self.parent.panes()[0])

        # wait until everything is packed and re-set the packed Event
        # FIXME: sometimes self.mapped is set() BEFORE all tabs and labels have their final size
        self.view.after_idle(self.mapped.set)

        # TODO: now the size of the XYPlot might have changed - (how) is this recognized ?

    def viewmode_update(self, conf):
        view_buttons = { XYPlot: self.graph_button,
                         PVTable: self.table_button }
        for v in view_buttons:
            if conf.viewmode == v:
                view_buttons[v].config(relief=SUNKEN)
            else:
                view_buttons[v].config(relief=RAISED)

    def experiment_view_update(self, view):
        tab = self.tabs[view.experiment]
        for i in range(view.experiment.get_nvalues() + 1):
#            tab.valueboxes[i]....
            tab.colorbuttons[i].config(bg=view.colors[i], activebackground=view.colors[i])

    def choose_color(self, view, i):
        view.set_color(i, askcolor()[1])
        
    def add_tab(self, ox):
        tab = Frame(self)
        tab.valueboxes = {}
        tab.colorbuttons = {}

        for i in range(ox.get_nvalues() + 1):
    
            # Display Selection Checkboxes
            box = Checkbutton(tab, text=ox.get_desc(i))
            box.grid(row=i, column=0, sticky=W)
            tab.valueboxes[i] = box
            
            # Color Cooser Buttons
            #  -> creating a Button with image=... lets one specify with and height in pixels
            button = Button(tab, image=self.bi, width=10, height=10,
                            command=partial(self.choose_color, ox.view, i),
                            bg=ox.view.colors[i], activebackground=ox.view.colors[i])
            button.grid(row=i, column=1, padx=4, pady=4)
            tab.colorbuttons[i] = button

        # Additional Info Label
        label = Label(tab, text=self.get_details_text(ox), justify=LEFT)
        label.grid(columnspan=2, sticky=W)
        tab.label = label

        # get notified on resize
        tab.bind("<Configure>", self.config_handler)
#        tab.bind("<Map>", self.map_handler)
        tab.grid_columnconfigure(0, weight=1)
        tab.pack()

        # keep track of the whole tab and add it to our notebook
        self.tabs[ox] = tab
        self.notebook_region.add(tab, text="Exp %d" % ox.num)

    def config_handler(self, event):
        # FIXME: see comment in ox_update()
        if not self.mapped.is_set():        # react only to user input events and not those
            return                          # which occur during the gui elements lay-ont (window mapping) phase already

        for tab in self.tabs.values():
            tab.label.configure(wraplength=event.width)

# waiting for <Map> events instead of using tk.after_idle()
# doesn't solve the problem described in ox_update() either
#    def map_handler(self, event):
#        print event

    @classmethod 
    def get_details_text(cls, ox):
        """return actor_name, date and ev. additional_details from OpenExperiment"""

        # Datum
        date = ox.get_date()
        YYYY = date[0:4]
        MM = date[4:6]
        DD = date[6:8]
        text = "Datum: %s.%s.%s" % ( DD, MM, YYYY )
        text += "\n\n"

        # Gruppe: Namen
        actor_name = ox.get_actor_name()
        text += "Gruppe: %s" % actor_name
        text += "\n\n"

        try:
            # Zusätzliche Informationen (z.b. Federkonstante)
            text += ox.get_additional_info()
        except:
            pass

        return text
        
        # import tkColorChooser
        # tkColorChooser.askcolor()
        # http://infohost.nmt.edu/tcc/help/pubs/tkinter/dialogs.html#tkColorChooser
