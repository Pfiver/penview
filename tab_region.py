# encoding: utf-8

from Tkinter import *
from itertools import count
from threading import Event
from functools import partial
from tkColorChooser import askcolor

from ttk import Notebook

from model import *

class TabRegion(Frame):
    def __init__(self, parent, window):
        Frame.__init__(self, parent)

        if not isinstance(parent, PanedWindow):
            raise InternalError("parent must be a PanedWindow")

        self.parent = parent    # parent is a PanedWindow
        self.window = window

        self.tabs = {}
        self.mapped = Event()           # are we packed ?

        window.conf.add_ox_listener(self.ox_update)

        # Tabs in notebook_region
        self.notebook_region = Notebook(self)
        
        # Graph and Table Buttons in switch_region
        self.switch_region = Frame(self)
        self.graph_button = Button(self.switch_region, text="Graph", command=lambda: window.do(PVAction.show_graph))
        self.table_button = Button(self.switch_region, text="Table", command=lambda: window.do(PVAction.show_table))
        self.graph_button.pack(side=LEFT, fill=X, expand=YES)
        self.table_button.pack(side=LEFT, fill=X, expand=YES)
        window.conf.add_viewmode_listener(self.viewmode_update)

        # pack()
        self.notebook_region.pack(fill=BOTH, expand=1)
        self.switch_region.pack(fill=X, side=BOTTOM)

        # once all gui elements are mapped, record that fact
        window.after_idle(self.mapped.set)                # at this point, ui.tk is known to be instantiated

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
                ox.views[self.window].add_listener(self.view_update)

        # re-add ourselves to the parent PanedWindow Widget
        # this will resize the tab_region to make all elements all tabs fit
        self.parent.remove(self)
        self.parent.add(self, before=self.parent.panes()[0])

        # wait until everything is packed and re-set the packed Event
        # FIXME: sometimes self.mapped is set() BEFORE all tabs and labels have their final size
        self.window.after_idle(self.mapped.set)

        # TODO: now the size of the XYPlot might have changed - (how) is this recognized ?

    def view_update(self, view):
        tab = self.tabs[view.ox]
        for i in range(view.ox.get_nvalues() + 1):
#            tab.valueboxes[i]....
            tab.colorbuttons[i].config(bg=view.colors[i], activebackground=view.colors[i])

    def viewmode_update(self, conf):
        if conf.viewmode == ViewMode.graph:
            self.graph_button.config(relief=SUNKEN)
            self.table_button.config(relief=RAISED)
        elif conf.viewmode == ViewMode.table:
            self.table_button.config(relief=SUNKEN)
            self.graph_button.config(relief=RAISED)

    def choose_color(self, view, i):
        view.set_color(i, askcolor()[1])

    def choose_values(self, view, i, v, *ign):
        if v.get():
            view.add_y_values(i)
        else:
            view.remove_y_values(i)

    def add_tab(self, ox):
        tab = Frame(self)
        tab.valueboxes = {}
        tab.colorbuttons = {}

        for i in range(ox.get_nvalues() + 1):
            view = ox.views[self.window]
            state = { True: NORMAL, False: DISABLED }[ i != self.window.conf.x_values ]

            # Display Selection Checkboxes
            v = BooleanVar(value=i in [self.window.conf.x_values] + list(view.y_values))
            v.trace("w", partial(self.choose_values, view, i, v))
            box = Checkbutton(tab, text=ox.get_desc(i), variable=v, state=state)
            box.grid(row=i, column=0, sticky=W)
            tab.valueboxes[i] = box
            
            # Color Cooser Buttons
            #  -> creating a Button with image=... lets one specify with and height in pixels
            button = Button(tab, image=self.bi, width=10, height=10,
                            command=partial(self.choose_color, view, i),
                            background=view.colors[i], activebackground=view.colors[i], state=state)
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
        self.notebook_region.add(tab, text="Exp %d" % ox.id)

    def config_handler(self, event):
        # FIXME: see comment in ox_update()
        if not self.mapped.is_set():        # react only to user input events and not those
            return                          # which occur during the gui elements lay-ont (window mapping) phase already

        for tab in self.tabs.values():
            tab.label.configure(wraplength=event.width)

#    # waiting for <Map> events instead of using tk.after_idle() doesn't solve the problem described in ox_update() either
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
