# encoding: utf-8

from random import *
from Tkinter import *
from threading import Thread, Event

from penview import *
from tab_region import TabRegion
from data_region import DataRegion

class PVWindow(Thread):
    def __init__(self, conf):
        Thread.__init__(self)
        self.conf = conf
        self.controller = None
        self.init = Event()     # clear until run() has initialized all widgets
        self.idle = Event()     # usually set
        self.idle.set()

    def run(self):
        # tk object
        self.tk = Tk() # the main window
        self.tk.minsize(800, 600)

        ## top-level widget
        self.frame0 = Frame(self.tk) # top-level container widget

        ## menubar
        self.menu_bar = Menu(self.tk)

        ### file menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open...", command=lambda: self.do(PVAction.open_exp))
        self.file_menu.add_command(label="Import...", command=lambda: self.do(PVAction.import_exp))
        self.file_menu.add_command(label="Quit", command=lambda: self.do(PVAction.quit_app))
    
        ### help menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Contents", command=lambda: self.do(PVAction.show_help))
        self.help_menu.add_command(label="About", command=lambda: self.do(PVAction.show_about))
    
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        ## main widget with vertical "splitter" bar
        self.main_region = PanedWindow(self.frame0, sashwidth=4)

        ## TAB is on the left
        self.tab_region = TabRegion(self.main_region, self)

        ## DATA is on the right
        self.data_region = DataRegion(self.main_region, self)

        ## 1. pack() then -> 2. add()  -- Reihenfolge beachten!
        self.tab_region.pack(fill=BOTH, expand=1)
        self.data_region.pack(fill=BOTH, expand=1)
        
        ## add()
        self.main_region.add(self.tab_region)
        self.main_region.add(self.data_region)

        # bind our map handler
#        self.xy_plot.bind("<Map>", self.map_handler)

        # pack top-level widget
        self.frame0.pack(fill=BOTH, expand=1)

        # pack main widget
        self.tk.config(menu=self.menu_bar)
        self.main_region.pack(fill=BOTH, expand=1)

        self.conf.set_viewmode(self.conf.viewmode)

        self.init.set()
        self.tk.mainloop()
    
    def stop(self):
        if self.is_alive():
            self.tk.quit()

    def wait_idle(self):
        self.init.wait()                 # possibly wait for run() to instantiate Tk and call its mainloop() first
        self.after_idle(self.idle.set)   # arrange for the "idle" Event to be set once tk.mainloop() is idle
        self.idle.wait()                 # wait for it
        self.idle.clear()                # the ui is usually considered busy

    def after_idle(self, action):
        self.tk.after_idle(action)

    def do(self, action):
        if not self.controller:
            raise Exception("Do it yourself!")
        else:
            self.controller.q(action)

    def set_controller(self, controller):
        self.controller = controller

    def map_handler(self, event):
        # Here we'd have to check the original height of the
        # top-level frame and subtract the height of the xy_plot
        # to find out how much space the buttons take u, height=50p
        # - but we use scrollbars now anyway and don't resize the xy_plot canvas on window resize
        pass
#        print event.widget.__class__
#        print "w: %d" % self.frame0.winfo_width()
#        print "W: %d" % self.xy_plot.winfo_width()
#        print "h: %d" % self.frame0.winfo_height()
#        print "H: %d" % self.xy_plot.winfo_height()
