#!/usr/bin/python
# encoding: utf-8
#
# Authors:
#    Tobias Thüring <tobias.thuering@students.fhnw.ch>
#    Patrick Pfeifer <patrick.pfeifer@students.fhnw.ch>
#
# December 2010 / January 2011
#
# Copyleft GNU GPL version 3 or any later version: read the file COPYRIGHT
#  the latest version is available here: http://www.gnu.org/licenses/gpl.html
#
# the product homepage is http://p2000.github.com/penview
# the source code is on github.com at https://github.com/P2000/penview
# the latest version can be git-cloned from git://github.com/P2000/penview.git
# an epyDoc generated api documentation is available at http://p2000.github.com/penview/epydoc
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
try:
    app_version = open(".version").read()
except IOError:
    app_version = "unknown (.version file missing)"

# debug infrastructure
#  FIXME: next time use the "logging" module
#
debug_flag = False

#  if debug_flag is True or penview is run with a "-debug" argument,
#  then debug() is redefined later on
def debug(*args): pass

# "public static void main"
#
# the if clause makes it possible for this file to serve two purposes at once:
#  1. as the container of applications main method
#  2. as a general "header" file that can be imported by all modules of the application
#
if __name__ == "__main__":

    # import this file as a module once, so we can adjust some global variables
    #  Every module is imported only _once_ only by one
    #  python interpreter instance and kept in the sys.modules dictionary.
    #  After importing a module you can set variables on it. Then other modules,
    #  imported by the current module, that import the module _again, will see the changed values.
    #  - "from module import symbol" and then assigning to symbol doesn't work !
    #  - check dev/global_vars for an in-depth investigation of the import mechanics
    import penview

    # debug infrastructure - part 2
    #
    import sys
    if debug_flag or (len(sys.argv) > 1 and sys.argv[1] == "-debug"):
        import os
        def debug(*args):
            if not len(args):
                args=("",) 
            elif type(args[0]) != str:
                args = (" | ".join(str(arg) for arg in args),)
            frame = sys._getframe(1); func = frame.f_code.co_name
            if 'self' in frame.f_locals: func = frame.f_locals['self'].__class__.__name__ + "." + func
            print "(%s:%d) in %s(): %s" % (os.path.basename(frame.f_code.co_filename), frame.f_lineno, func, args[0] % args[1:])
        # allways remember to FIRST "import penview" and THEN set penview.debug{,_flag} - as discussed above
        penview.debug = debug
        penview.debug_flag = debug_flag = True

    # Mac OS/X has a really touchy Python to Tkinter bridge
    #  it insists in Tk() (and Tk.mainloop()) being called from the "main" thread
    #  this forced us to use our formerly mostly idle main thread as the PVWindow thread,
    #  which in turn makes it necessary to keep a reference to that main thread in this variable
    #  the variable will be available in locals() of any module doing an "from penview import *" AFTER the following assignment
    # same story here: keep the assignment ABOVE "from window import PVWindow" because PVWindow won't see it otherwise - as discussed above
    import threading
    penview.tk_thread = threading.current_thread()

    # import the main modules
    from model import PVConf                   # FIXME: we might want to check if python-tk is installed,
    from window import PVWindow                #  as on a standard ubuntu maverick system it is seemingly NOT installed by default
    from controller import PVController        #  ... in case it is not and we're on a debian system, suggest the user to "sudo apt-get install python-tk"
 
    # say hi
    print "Welcome to %s!" % app_name

    # instantiate the different parts of the application
    conf = PVConf()                    # Model
    window = PVWindow(conf)               # View
    controller = PVController(conf, window)  # Controller

    # start the controller thread which, amongst other things, opens new files in the background
    controller.start()

    # and call PVWindow.main() which will end up in Tk.mainloop()
    window.main()

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
