# encoding: utf-8

from Tkinter import *
from Queue import Queue
from functools import partial
from threading import Thread, Event

from penview import *
from tab_region import TabRegion
from data_region import DataRegion

class PVWindow(Thread):
    def __init__(self, conf):
        Thread.__init__(self)
        self.conf = conf
        self.controller = None
        self.tk_q = Queue()
        self.init = Event()     # clear until run() has initialized all widgets
        self.idle = Event()     # set unless somebody calls wait_idle()
        self.idle.set()

    def run(self):
        # tk object
        self.tk = Tk() # the main window
        self.tk.minsize(800, 600)
        self.tk.title(app_name)

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

        # pack() top-level widget
        self.frame0.pack(fill=BOTH, expand=1)

        # pack() main widget
        self.tk.config(menu=self.menu_bar)
        self.main_region.pack(fill=BOTH, expand=1)

        # set the default viewmode to make the window look more interresting
        self.conf.set_viewmode(self.conf.viewmode)

        # bind out private virtual thread context switch helper event handler
        self.tk.bind("<<PVEvent>>", self.tk_do_cb)

        # register the fact that everything is set up now
        self.init.set()

        # call Tk.mainloop()
        self.tk.mainloop()
        
        # make sure the controller to quit
        self.do(PVAction.quit_app)

    def stop(self):
        if self.is_alive():
            self.tk.quit()

    def wait_idle(self):
        "wait until the Tk.mainloop() thread is idle i.e. no more events are pending"
        self.init.wait()                 # possibly wait for run() to instantiate Tk and call its mainloop() first
        self.after_idle(self.idle.set)   # arrange for the "idle" Event to be set once tk.mainloop() is idle
        self.idle.wait()                 # wait for it
        self.idle.clear()                # the ui is usually considered busy

    def after_idle(self, action):
        "schedule a function to be called by the tk.mainloop() thread as soon as it is idle - the calling thread returns immediately"
        self.tk_do(self.tk.after_idle, action)              # do a context switch

    def tk_do(self, task, *args):
        "switch thread context to the Tk.mainloop() thread and let task(*args) be called from there"
        print task
        self.tk_q.put(partial(task, *args))                 # create a function closure and safe a reference
        self.tk.event_generate("<<PVEvent>>", when='tail')  # queue a <<PVEvent>> on the Tk.mainloop() that will cause the closure to be called

    def tk_cb(self, task):
        "return a function closure thatwhen called will arrange for 'task' being called from the Tk.mainloop() thread"
        return partial(self.tk_do, task)

    def tk_do_cb(self, event):
        "call the current self.tk_task"
        if self.tk_q.empty():
            raise Exception("Nothing to do")
        return self.tk_q.get()()

    def do(self, action):
        if not self.controller:
            raise Exception("No controller")
        else:
            self.controller.q(action)

    def set_controller(self, controller):
        self.controller = controller