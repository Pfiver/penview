from Queue import Queue
from threading import Thread

from penview import *

class PVController(Thread):
    
    def __init__(self, ui):
        Thread.__init__(self)
        self.ui = ui
        self.action_q = Queue()

    def run(self):
        while True:
            a = self.dq()
            if a == PVAction.Quit:
                self.ui.stop()
                break
            print a

    def q(self, action):
        self.action_q.put(action)

    def dq(self):
        return self.action_q.get()
