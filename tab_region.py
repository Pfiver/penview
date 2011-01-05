# encoding: utf-8

from Tkinter import *
from itertools import count
from threading import Event
from functools import partial
from tkColorChooser import askcolor

import platform
if platform.system() == 'Darwin':
    import os
    os.environ['TILE_LIBRARY'] = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'), 'tile0.8.3')
from lib.ttk import Notebook

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

        window.conf.add_ox_listener(window.tk_cb(self.ox_update))

        # Tabs in notebook_region
        self.notebook_region = Notebook(self)

        # Graph and Table Buttons in switch_region
        self.switch_region = Frame(self)
        self.graph_button = Button(self.switch_region, text="Graph", command=lambda: window.do(PVAction.show_graph))
        self.table_button = Button(self.switch_region, text="Table", command=lambda: window.do(PVAction.show_table))
        self.graph_button.pack(side=LEFT, fill=X, expand=YES)
        self.table_button.pack(side=LEFT, fill=X, expand=YES)
        window.conf.add_viewmode_listener(window.tk_cb(self.viewmode_update))

        # pack()
        self.notebook_region.pack(fill=BOTH, expand=1)
        self.switch_region.pack(fill=X, side=BOTTOM)

        # once all gui elements are mapped, record that fact
#        window.after_idle(self.mapped.set)

    def ox_update(self, conf):
        # clear the mapped Event (used by config_handler())
        # as we are going to add and resize some elements now
        self.mapped.clear()
        
        for ox in conf.open_experiments:
            if ox not in self.tabs:
                self.add_tab(ox)
                ox.views[self.window].add_listener(self.window.tk_cb(self.view_update))

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
        for i in range(view.ox.nvalues + 1):
#            tab.valueboxes[i]....
            tab.colorbuttons[i].image.config(foreground=view.colors[i])

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

        # Display Experiment Name
        exp_name = Label(tab, text=ox.get_exp_name(), font=13)
        exp_name.grid(row=0, sticky=W)
        tab.exp_name = exp_name

        for i in range(ox.nvalues + 1):
            view = ox.views[self.window]
            state = { True: NORMAL, False: DISABLED }[ i != self.window.conf.x_values ]

            # Display Selection Checkboxes
            v = BooleanVar(value=i in [self.window.conf.x_values] + list(view.y_values))
            v.trace("w", partial(self.choose_values, view, i, v))
            box = Checkbutton(tab, text=ox.get_desc(i), variable=v, state=state)
            box.grid(row=i+1, column=0, sticky=W)
            tab.valueboxes[i] = box
            
            # Color Cooser Buttons
            #  -> creating a Button with image=... lets one specify with and height in pixels
            #  -> for mac's aqua surface, we need a real pixmap because the button ignores all background="color" options
            # allways keep a reference to some the BitmapImage because if you don't,
            # the BitmapImage object will be reaped by the garbage collector and the button doesn't work
            w = h = 10
            BITMAP = "#define im_width %d\n#define im_height %d\n" % (w, h)
            BITMAP += "static char im_bits[] = {\n" + ",".join("255" for i in range(w*h)) + "\n};\n"
            bi = BitmapImage(data=BITMAP, foreground=view.colors[i])
            button = Button(tab, image=bi, width=10, height=10, command=partial(self.choose_color, view, i), state=state)
            button.grid(row=i+1, column=1, padx=4, pady=4)
            tab.colorbuttons[i] = button
            button.image = bi

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

    @staticmethod
    def get_details_text(ox):
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
