#!/usr/bin/python
# encoding: utf-8
#
# Authors:
#    Tobias Thüring
#    Patrick Pfeifer
#
# December 2010
#    
# Copyleft GNU GPL version 3 or any later version:
#    http://www.gnu.org/licenses/gpl.html
#
# the latest version of this code can be found on github:
#    https://github.com/P2000/penview
# (EpyDoc generated) documentation is available on wuala:
#    http://content.wuala.com/contents/patrick2000/Shared/school/11_Projekt/Pendulum/Dokumentation/DB%20V3.pdf?dl=1
#

# actions the controller knows how to handle
#
class PVAction:
    open_exp, import_exp, quit_app, show_help, show_about, show_table, show_graph, reset_scale = range(8)

    # a function to map an action number to its name
    #
    @classmethod
    def name(cls, number):
        for attr in cls.__dict__:
            if getattr(cls, attr) == number:
                return attr

# the possible experiment view modes
#
class ViewMode:
    graph, table = range(2)

# name and version of this application
#
app_name = "PenView"
app_version = "1.0-rc3"

# debug infrastructure
#  FIXME: next time use "logging" module
#
debug_flag = False

#  if debug_flag is True or penview is run with a "-debug" argument,
#  debug() is redefined later on
def debug(*args): pass

# "public static void main"
#
# the if clause makes it possible for this file to serve two purposes at once:
#  1. as the container of applications main method
#  2. as a general "header" file that can be imported by all modules of the application
#
if __name__ == "__main__":

    # import this file as a module once, so we can adjust some global variables
    #  every module is imported only once into each python interpreter instance and lands in the sys.modules dictionary
    #  after importing a module once you can set variables on it and other modules imported from the current module that import
    #  the module again, will see the changed values
    import penview

    # debug infrastructure - part 2
    #
    import sys
    if debug_flag or (len(sys.argv) > 1 and sys.argv[1] == "-debug"):
        import os
        def debug(*args):
            if len(args) and type(args[0]) != str:
                args = (" - ".join(str(arg) for arg in args),)
            frame = sys._getframe(1); func = frame.f_code.co_name
            if 'self' in frame.f_locals: func = frame.f_locals['self'].__class__.__name__ + "." + func
            print "(%s:%d) in %s(): %s" % (os.path.basename(frame.f_code.co_filename), frame.f_lineno, func, args[0] % args[1:])

        # this is delicate as well: you have to "import penview" FIRST and THEN set penview.debug{,_flag}
        #  - "from penview import debug" doesn't work
        #  - check dev/global_vars for full investigation
        penview.debug = debug
        penview.debug_flag = debug_flag = True

    # Mac OS/X has a really touchy Python to Tkinter bridge
    #  it insists in Tk() (and Tk.mainloop()) being called from the "main" thread
    #  this forced us to use our formerly mostly idle main thread as the PVWindow thread
    #  which in turn makes it necessary to keep a reference to that main thread in this variable
    #  the variable will be available in locals() of any module doing an "from penview import *" AFTER the following assignment
    #  (therefore keep the assignment ABOVE "from window import PVWindow" because PVWindow won't see it otherwise)
    #
    import threading
    penview.tk_thread = threading.current_thread()

    # import the main modules
    from model import PVConf				# FIXME: we need to check if python-tk is installed, as on a standard ubuntu maverick
    from window import PVWindow				# system it is seemingly NOT installed by default
    from controller import PVController		#  ... in case it is not and we're on a debian system, suggest "sudo apt-get install python-tk"
 
    # say hi
    print "Welcome to %s!" % app_name

    # instantiate the different parts of the application
    conf = PVConf()                    # Model
    window = PVWindow(conf)               # View
    controller = PVController(conf, window)  # Controller

    # start the controller thread which, amongst other things, opens new files in the background
    controller.start()

    # and run the PVWindow (thread) which will end up in Tk.mainloop()
    window.run()

    # FIXME: this block is a victim of the super-touchy OS/X Python to Tkinter bridge
    # for easy debugging during the development phase, automatically open some experiments
    # the storage path of experiments being opened are defined in dialogs.py in OpenWizard in "examples"
#    if debug_flag:
#        controller.wait_idle()
#        controller.q(PVAction.open_exp)
#        controller.q(PVAction.open_exp)

    # wait for the controller finish
    controller.join()
    
    # say bye
    print "Good Bye - Hope to se you again!"
