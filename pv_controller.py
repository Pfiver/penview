from Queue import Queue
from threading import Thread

from penview import *
from file_wizard import *

class PVController(Thread):
    
    def __init__(self, ui, conf):
        Thread.__init__(self)
        self.ui = ui
        self.conf = conf
        self.action_q = Queue()

    def run(self):
        self.run = True
        while self.run:
            a = self.dq()
            try:
                self.get_handler(a)()
            except Exception, e:
                print "Exception in PVController.run(): %s" % str(e)

    def stop(self):
        self.run = False

    def q(self, action):
        self.action_q.put(action)

    def dq(self):
        return self.action_q.get()

    def get_handler(self, action):
        try:
            return getattr(self, "do_" + pvaction_name[action].lower())
        except AttributeError:
            raise Exception("Sorry, '%s' is not yet implemented" % pvaction_name[action])

    def do_quit(self):
        self.ui.stop()
        self.stop()

    def do_open(self):
        wizard = OpenWizard()
        
    def do_import(self):
        wizard = ImportWizard()
