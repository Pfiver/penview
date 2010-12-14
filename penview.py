class PVAction:
    Open, Import, Quit, Help, About = range(5)

if __name__ == "__main__":

    # say hi
    print "Welcome to PenView!"

    # import and instantiate and connect application parts (Model-View-Controller)
    from penview_ui import PenViewUI
    from pv_controller import PVController

    ui = PenViewUI()
    controller = PVController(ui)

    ui.set_controller(controller)

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