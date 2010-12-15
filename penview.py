class PVAction:
    Open, Import, Quit, Help, About = range(5)

pvaction_name = dict(map(lambda name: (getattr(PVAction, name), name),
                         filter(lambda a: not a.startswith('_'), dir(PVAction))))

debug_flag = 1
def debug(*args):
    if not debug_flag:
        return
    import sys
    if len(args) < 1: args=[""]
    print sys._getframe(1).f_code.co_name + ": " + args[0] % args[1:]

if __name__ == "__main__":

    # say hi
    print "Welcome to PenView!"

    # import and instantiate and connect application parts (Model-View-Controller)
    from penview_ui import PenViewUI
    from pv_controller import PVController
    from penview_model import PenViewConf

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
    
    # queue a test action
    controller.q("ACTION!")

    # wait for gui thread (exits when the main window gets closed)
    ui.join()
    controller.q(PVAction.Quit)
    print "Good Bye - Hope to se you again!"