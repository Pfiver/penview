from random import *
from Tkinter import *
from threading import Thread

from penview import *
from tab_region import TabRegion
from data_region import DataRegion

# The "view"
class PenViewUI(Thread):

    def run(self):
        # tk object
        self.tk = Tk() # the main window

        # level 0 widget
        self.frame0 = Frame(self.tk) # top-level container widget

        # level 0 widgets
        ## Menu Bar Initialization
        self.menu_bar = Menu(self.tk)
        ## File Menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open...", command=lambda: self.controller.q(PVAction.Open))
        self.file_menu.add_command(label="Import...", command=lambda: self.controller.q(PVAction.Import))
        self.file_menu.add_command(label="Quit", command=lambda: self.controller.q(PVAction.Quit))
        ## Help Menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Contents", command=lambda: self.controller.q(PVAction.Help))
        self.help_menu.add_command(label="About", command=lambda: self.controller.q(PVAction.About))
        ## Associate File Help with Menu Bar
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        ## Initialize Splitter/PanedWindow
        self.main_region = PanedWindow(self.frame0, showhandle=1)
        ## TAB is on the left
        self.tab_region = TabRegion(self.main_region, self.conf)

        ## DATA is on the right
        self.data_region = DataRegion(self.main_region)

        ## 1. pack() then -> 2. add() Reihenfolge beachten!
        self.tab_region.pack(fill=BOTH, expand=1)
        self.data_region.pack(fill=BOTH, expand=1)
        
        ## add()
        self.main_region.add(self.tab_region)
        self.main_region.add(self.data_region)
        # bind our map handler
#        self.xy_plot.bind("<Map>", self.map_handler)

        # pack level 0 widget
        self.frame0.pack(fill=BOTH, expand=1)

        # pack level 1 widgets
#        self.button_region.pack_propagate(0)
#        self.button_region.pack(fill=None, expand=0)
        self.tk.config(menu=self.menu_bar)
        self.main_region.pack(fill=BOTH, expand=1)

        # pack level 2 widget
        self.tk.mainloop()
    
    def stop(self):
        if self.is_alive():
            self.tk.quit()

    def set_conf(self, conf):
        self.conf = conf

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

