# encoding: utf-8

from Tkinter import *
from Queue import Queue
from functools import partial
from threading import Event, current_thread

from penview import *
from model import PVConf
from tab_region import TabRegion
from data_region import DataRegion

class PVWindow:
    def __init__(self):
        self.conf = PVConf(self)
        self.controller = None
        self.tk_do_q = Queue()  # a queue of things we have to do (function closures)
        self.tk_do_ret = {}     # a dictionary of Event objects to indicate something is done,
                                # accompanied by return values and possible exceptions
        self.alive = Event()     # clear until run() has initialized all widgets and after tk.mainloop() returned
        self.idle = Event()     # set unless somebody calls wait_idle()
        self.idle.set()

    def main(self):
        # the root widget
        self.tk = Tk()

        self.tk.title(app_name)
        self.tk.minsize(800, 600)
        self.tk.protocol("WM_DELETE_WINDOW", lambda: self.do(PVAction.quit_app))

        # top-level widget
        self.frame0 = Frame(self.tk)

        # menubar
        self.menu_bar = Menu(self.tk)

        ## file menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open...",     command=lambda: self.do(PVAction.open_exp))
        self.file_menu.add_command(label="Import...",   command=lambda: self.do(PVAction.import_exp))
        self.file_menu.add_command(label="Quit",        command=lambda: self.do(PVAction.quit_app))

        ## view menu
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Reset Scale", command=lambda: self.do(PVAction.reset_scale), state=DISABLED)

        ### this function en- or disables the "Reset Scale" menu entry
        def vm_listener(conf):
            if len(conf.open_experiments) > 0 and conf.viewmode == ViewMode.graph:
                self.view_menu.entryconfig(0, state=NORMAL)
            else:
                self.view_menu.entryconfig(0, state=DISABLED)

        ### register our viewmode_listener
        self.conf.add_ox_listener(self.tk_cb(vm_listener))
        self.conf.add_viewmode_listener(self.tk_cb(vm_listener))

        ## help menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="Contents",    command=lambda: self.do(PVAction.show_help))
        self.help_menu.add_command(label="About",       command=lambda: self.do(PVAction.show_about))
    
        ## add the menues to the menubar
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        # main widget with vertical "splitter" bar
        ## frame0 currently contains only this widget but might hold a tool- and/or menubar as well in the future
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

        # set the default viewmode to make the window look more interesting
        #  TODO: keep an eye on this - it used not to work after changing tk_thread to be the main thread and
        #  PVWindow still extending the Thread class, .... i think :-) 
        self.conf.set_viewmode(self.conf.viewmode)

        # bind out virtual private event to the thread context switch helper event handler
        self.tk.bind("<<PVEvent>>", self.tk_do_handler)

        # register the fact that everything is set up now
        self.alive.set()

        # call Tk.mainloop()
        self.tk.mainloop()

        self.alive.clear()

    def stop(self):
        if self.alive.is_set():             # FIXME: queue the request if self exists but is not yet alive
            self.tk_do(self.tk.quit)        # do a context switch if necessary

    def wait_idle(self):
        "wait until the Tk.mainloop() thread is idle i.e. no more events are pending"
        self.alive.wait()                 # possibly wait for run() to instantiate Tk and call its mainloop() first
        self.after_idle(self.idle.set)   # arrange for the "idle" Event to be set once tk.mainloop() is idle
        self.idle.wait()                 # wait for it
        self.idle.clear()                # the ui is usually considered busy

    def after_idle(self, action):
        "schedule a function to be called by the tk.mainloop() thread as soon as it is idle - the calling thread returns immediately"
        self.tk_do(self.tk.after_idle, action)              # do a context switch if necessary

    def tk_do(self, task, *args):
        "call task(*args) from the PVWindow/Tk.mainloop() thread"
        if current_thread() == tk_thread:                   # already in the right thread
            return task(*args)                              # just call the function - otherwise we have to switch
        method = partial(task, *args)                       # create a closure to call the function with the specified arguments
        self.tk_do_q.put(method)                            # and queue that to be called in the <<PVEvent>> handler, tk_do_handler()
        self.tk_do_ret[method] = Event()                    # plus, use the reference as a key to the tk_do_ret dictionary and insert an Event()
        self.tk.event_generate("<<PVEvent>>", when='tail')  # queue a virtual Event for the Tk.mainloop()
        self.tk_do_ret[method].wait()                       # now wait for the handler to be called and event to be set
        e = self.tk_do_ret[method].exception                # safe the exceptions produced by the closure (if any)
        ret = self.tk_do_ret[method].value                  # and the return value
        del self.tk_do_ret[method]                          # and delete the event
        if e: raise type(e), e, e.tb                        # if an exception occured, raise here it the calling thread - otherwise go ahead
        return ret                                          # return the return value

    def tk_do_handler(self, event):
        "call the current self.tk_task"
        method = self.tk_do_q.get_nowait()                  # remove one task from the queue
        self.tk_do_ret[method].value = None
        self.tk_do_ret[method].exception = None
        try:
            self.tk_do_ret[method].value = method()         # execute the method and safe the return value
        except Exception, e:
            import sys
            e.tb = sys.exc_info()[2]
            self.tk_do_ret[method].exception = e
        finally:
            self.tk_do_ret[method].set()                    # record the fact that the method has returned

    def tk_cb(self, task):
        "return a function closure, that, when called, will schedule 'task' to be called from the Tk.mainloop() thread"
        return partial(self.tk_do, task)

    def do(self, action):
        "tells the controller to perform the specified action and returns immediately"
        if not self.controller:
            raise Exception("No controller")
        else:
            self.controller.q(action)

    def set_controller(self, controller):
        "tell this window who's controlling it"
        self.controller = controller
