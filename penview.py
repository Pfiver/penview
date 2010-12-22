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

debug_flag = True

import sys
from os import path

def debug(*args):
    if not debug_flag:
        return
    f = sys._getframe(1)
    if len(args) < 1: args = [""]
    print "%s: %s(): %s" % (f.f_locals.values()[0].__class__, f.f_code.co_name, args[0] % args[1:])

sys.path.append(path.join(path.dirname(sys._getframe().f_code.co_filename), "lib"))

if __name__ == "__main__":

    # say hi
    print "Welcome to PenView!"

    # import and instantiate and connect application parts (Model-View-Controller)
    from penview_ui import PenViewUI
    from penview_model import PenViewConf
    from pv_controller import PVController

    ui = PenViewUI()                    # View
    conf = PenViewConf()                # Model
    controller = PVController(ui, conf) # Controller

    ui.set_conf(conf)
    ui.set_controller(controller)
    conf.set_controller(controller)

    # noisily start helper the part's threads
    ui.start()
    print "UI Running"
    
    controller.start()
    print "Controller Running"

    if debug_flag:
        controller.dispatch_events()
        controller.q(PVAction.open_exp)
        controller.q(PVAction.open_exp)
    #    controller.q(PVAction.open_exp)

    # wait for gui thread (exits when the main window gets closed)
    ui.join()
    controller.q(PVAction.quit_app)
    print "Good Bye - Hope to se you again!"