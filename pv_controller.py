from Queue import Queue
from threading import Thread
from traceback import print_exc
from tkMessageBox import showerror

from penview import *
from file_wizard import *
from penview_model import *
from data_region import XYPlot, PVTable

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
                print "Exception in PVController.run(): " + str(e)
                showerror(app_name, str(e))
                if debug_flag:
                    print_exc()
            finally:
                self.task_done()

    def stop(self):
        self.run = False

    def q(self, action):
        self.action_q.put(action)

    def dq(self):
        return self.action_q.get()

    def task_done(self):
        self.action_q.task_done()

    def wait_idle(self):
        self.action_q.join()

    def get_handler(self, action):
        try:
            return getattr(self, "do_" + pvaction_name[action])
        except AttributeError:
            raise Exception("Sorry, '%s' is not yet implemented" % pvaction_name[action])

    def do_quit_app(self):
        self.ui.stop()
        self.stop()

    def do_open_exp(self):
        self.open_helper(OpenWizard.open_experiment())

    def do_import_exp(self):
        self.open_helper(ImportWizard.open_experiment())

    def open_helper(self, ox):
        self.conf.add_open_experiment(ox)

    def do_show_table(self):
        self.conf.set_view(PVTable)
        
    def do_show_graph(self):
        self.conf.set_view(XYPlot)

    def dispatch_events(self):
        self.ui.wait_idle()
        self.wait_idle()


