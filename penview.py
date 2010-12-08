from penview_ui import *
from threading import Thread

class PenView:

    def __init__(self):
        self.event_handler = Thread(target=self.showtime)
        self.event_handler.start()
        print "Welcome to PenView!"

    def showtime(self):
        self.ui = PenViewUI()
        self.ui.handle_events()
        print "Good Bye - Hope to se you again!"

PenView()