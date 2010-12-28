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

class PVAction:
    open_exp, import_exp, quit_app, show_help, show_about, show_table, show_graph = range(7)
        
pvaction_name = dict((getattr(PVAction, a), a) for a in PVAction.__dict__)

class ViewMode:
    graph, table = range(2)

app_name = "PenView"

debug_flag = True

if not debug_flag:
    def debug(*args):
        pass
else:
    import sys
    def debug(*args):
        if len(args) and type(args[0]) != str:
            args = " - ".join(str(arg) for arg in args)
        f = sys._getframe(1)
        line = f.f_lineno
        func = f.f_code.co_name
        file = f.f_code.co_filename
        class_ = f.f.f_locals.values()[0].__class__
        print "%s [%4d] in %s.%s(): %s" % (file, line, class_, func, args[0] % args[1:])

if __name__ == "__main__":

    # say hi
    print "Welcome to %s!" % app_name

    # some import path trickery
    import os, sys
    print os.path.join(os.path.dirname(sys._getframe().f_code.co_filename), "lib")
    sys.path.append(os.path.join(os.path.dirname(sys._getframe().f_code.co_filename), "lib"))

    # import the main modules
    from model import PVConf
    from window import PVWindow
    from controller import PVController

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