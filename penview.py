class PVAction:
    Open, Import, Quit, Help, About = range(5)
        
pvaction_name = dict((getattr(PVAction, e), e) for e in PVAction.__dict__)

debug_flag = 1
def debug(*args):
    if not debug_flag:
        return
    import sys
    f = sys._getframe(1)
    if len(args) < 1: args = [""]
    print "%s: %s(): %s" % (f.f_locals.values()[0].__class__, f.f_code.co_name, args[0] % args[1:])

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

    # wait for gui thread (exits when the main window gets closed)
    ui.join()
    controller.q(PVAction.Quit)
    print "Good Bye - Hope to se you again!"