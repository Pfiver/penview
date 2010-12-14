class PVAction:
    Quit = range(1)

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
    print "Cotroller Running"
    
    # que a test action
    controller.q("ACTION!")

    # wait for helper threads (not really necessary)
    ui.join()
    controller.join()
    print "Good Bye - Hope to se you again!"