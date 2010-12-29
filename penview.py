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

# actions handled by the application controller
#
class PVAction:
    open_exp, import_exp, quit_app, show_help, show_about, show_table, show_graph = range(7)

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

# the name of this application
#
app_name = "PenView"

# debug infrastructure
#  FIXME: next time use "logging" module
#
debug_flag = True

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

    # some import path trickery
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(sys._getframe().f_code.co_filename), "lib"))

    # debug infrastructure - part 2
    #
    if debug_flag or (len(sys.argv) > 1 and sys.argv[0] == "-debug"):
        def debug(*args):
            if len(args) and type(args[0]) != str:
                args = " - ".join(str(arg) for arg in args)
            frame = sys._getframe(1); func = frame.f_code.co_name
            if 'self' in frame.f_locals: func = frame.f_locals['self'].__class__.__name__ + "." + func
            print "(%s:%d) in %s(): %s" % (os.path.basename(frame.f_code.co_filename), frame.f_lineno, func, args[0] % args[1:])

        # this is delicate as well: you have to "import penview" and then set penview.debug(_flag)
        #  - "from penview import debug" won't work
        #  - check mini-spikes/global_vars for full investigation
        import penview
        penview.debug = debug
        penview.debug_flag = debug_flag = True

    # import the main modules
    from model import PVConf
    from window import PVWindow
    from controller import PVController
 
    # say hi
    print "Welcome to %s!" % app_name

    # instantiate the different parts of the application
    conf = PVConf()                    # Model
    window = PVWindow(conf)               # View
    controller = PVController(conf, window)  # Controller

    # and start the threads
    window.start()
    controller.start()

    # for easy debugging during the development phase, automatically open some experiments
    # the storage path of experiments being opened are defined in dialogs.py in OpenWizard in "examples"
    if debug_flag:
        controller.wait_idle()
        controller.q(PVAction.open_exp)
        controller.q(PVAction.open_exp)

    # wait for the controller finish
    controller.join()
    
    # say bye
    print "Good Bye - Hope to se you again!"
