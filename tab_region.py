# encoding: utf-8

from Tkinter import *
from itertools import count
from threading import Event
from functools import partial
from tkColorChooser import askcolor

# aaaw
#
# Mac OS/X hack to make tkk.Notebook work - check the SRS for d
#
# Burnt about 8 man-hours. We wanted to make this work by any means.
# After we found the (presumeably) right libtile binary (OS/X .dylib, "universal" - e.g. intel and ppc) inside this .dmg here:
# http://downloads.activestate.com/ActiveTcl/releases/8.4.19.4/ActiveTcl8.4.19.4.292682-macosx-universal-threaded.dmg,
# the tcl interpreter would initially still not be happy, even though the binary was in the TILE_LIBRARY
# path. At that point we were about to give up. It took some mailing-lists browsing again until I finally
# realized that the interpreter was probably looking for and would load a .tcl script first, which would
# then (amongst other things) in turn load the binary library. And that turned out to be true. After copying
# the .tcl scripts from the .dmg into the TILE_LIBRARY path as well, the interpreter was finally happy.
# /We/ were still not /that/ happy, since we found out that OS/X ignored the Button(bgcolor=) attribute.
# But we found a fix for that in less than 2 hours (see below in add_tab()) 
#
import platform
if platform.system() == 'Darwin':
    import os
    os.environ['TILE_LIBRARY'] = os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib'), 'tile0.8.3')
from lib.ttk import Notebook
#
# aaaw off

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
        #  TODO: this statement also has to be watched closely
        #  same situation as with PVWindow.run(), "self.conf.set_viewmode(self.conf.viewmode)"
        window.after_idle(self.mapped.set)
                                              
    cb_w = cb_h = 10                                # color-chooser button width & height

    # http://en.wikipedia.org/wiki/X_BitMap:
    #  ... a single bit represents each pixel (black or white) ...
    #  ... If the image width does not match a multiple of 8,
    #  the display mechanism ignores and discards the extra bits in the last byte of each row. ...
    cb_x = 0 if cb_w // 8 == cb_w / 8.0 else 8
    bitmap_data = "#define im_width %d\n#define im_height %d\n" % (cb_w, cb_h)
    bitmap_data += "static char im_bits[] = {\n" + ",".join("255" for i in range((cb_w+cb_x)/8*cb_h)) + "\n};"

    def ox_update(self, conf):
        "PVConf.ox_listener callback function"
        # clear the mapped Event (used by config_handler())
        # as we are going to add and resize some elements now
        self.mapped.clear()
        
        for ox in conf.open_experiments:
            if ox not in self.tabs:
                self.add_tab(ox)
                ox.views[self.window].add_listener(self.window.tk_cb(self.view_update))

        # important !
        self.window.tk.update_idletasks()

        # re-add ourselves to the parent PanedWindow Widget
        # this will resize the tab_region to make all elements in all tabs fit
        for pane in self.parent.panes():
            self.parent.remove(pane)
            self.parent.add(pane)

        # wait until everything is packed and re-set the packed Event
        #  --- FIXME: sometimes self.mapped is set() BEFORE all tabs and labels have their final size ---
        #  ---> probably fixed by update_idletasks() call above
        self.window.after_idle(self.mapped.set)

        # TODO: now the size of the XYPlot might have changed - (how) is this recognized ?

    def view_update(self, view):
        "ExperimentView.listener callback function"
        tab = self.tabs[view.ox]

        for i in range(view.ox.nvalues + 1):
            if i != self.window.conf.x_values:
                tab.valueboxes[i].config(state=NORMAL)
                tab.colorbuttons[i].config(state=NORMAL)
            else:
                tab.valueboxes[i].config(state=DISABLED)
                tab.colorbuttons[i].config(state=DISABLED)
            tab.colorbuttons[i].image.config(foreground=view.colors[i])

    def viewmode_update(self, conf):
        "PVConf.viewmode_listener callback function"
        if conf.viewmode == ViewMode.graph:
            self.graph_button.config(relief=SUNKEN)
            self.table_button.config(relief=RAISED)
        elif conf.viewmode == ViewMode.table:
            self.table_button.config(relief=SUNKEN)
            self.graph_button.config(relief=RAISED)

    def choose_color(self, view, i):
        "color chooser buttons 'action=' event handler"
        view.set_color(i, askcolor()[1])

    def choose_values(self, view, i, v, *ign):
        "valueboxes checkboxes 'action=' event handler"
        if v.get():
            view.add_y_values(i)
        else:
            view.remove_y_values(i)

    def add_tab(self, ox):
        "tab setup"
        tab = Frame(self.notebook_region)
        tab.valueboxes = {}
        tab.colorbuttons = {}

        # Display Experiment Name
        label = Label(tab, text=ox.get_exp_name(), font=13, justify=LEFT, wraplength=300)
        label.grid(row=0, columnspan=2, sticky=W)
        tab.name_label = label

        for i in range(ox.nvalues + 1):
            view = ox.views[self.window]
            state = { True: NORMAL, False: DISABLED }[ i != self.window.conf.x_values ]

            # Display Selection Checkboxes
            v = BooleanVar(value=i in [self.window.conf.x_values] + list(view.y_values))
            v.set(i in set((self.window.conf.x_values,)) | ox.views[self.window].y_values)
            v.trace("w", partial(self.choose_values, view, i, v))
            box = Checkbutton(tab, text="%s (%s)" % (ox.get_desc(i), ox.get_units(i)), variable=v, state=state)
            box.grid(row=i+1, column=0, sticky=W)
            tab.valueboxes[i] = box

            # Color Cooser Buttons
            #  -> creating a Button with image=... lets one specify with and height in pixels
            #  -> for mac's aqua surface, we need a real pixmap because the button ignores all background="color" options
            # allways keep a reference to some the BitmapImage because if you don't,
            # the BitmapImage object will be reaped by the garbage collector and the button doesn't work
            bi = BitmapImage(data=self.bitmap_data, foreground=view.colors[i])
            button = Button(tab, image=bi, command=partial(self.choose_color, view, i), state=state)
            button.grid(row=i+1, column=1, padx=4, pady=4)
            tab.colorbuttons[i] = button
            button.image = bi

        # Additional Info Label
        label = Label(tab, text=self.get_details_text(ox), justify=LEFT, wraplength=300)
        label.grid(columnspan=2, sticky=W)
        tab.info_label = label

        # get notified on resize
        tab.bind("<Configure>", self.config_handler)
        tab.grid_columnconfigure(0, weight=1)
        tab.pack(side=TOP)

        # keep track of the whole tab and add it to our notebook
        self.tabs[ox] = tab
        self.notebook_region.add(tab, text="Exp %d" % ox.id)
        self.notebook_region.select(tab)

    def config_handler(self, event):
        "tab region resize event handler"
        if not self.mapped.is_set():        # react only to user input events and not those
            return                          # which occur during the gui elements lay-ont (window mapping) phase already

        # wrap the info labels
        for tab in self.tabs.values():
            tab.name_label.configure(wraplength=event.width)
            tab.info_label.configure(wraplength=event.width)

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
