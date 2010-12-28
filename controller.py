# encoding: utf-8

from Queue import Queue
from threading import Thread
from traceback import print_exc
from tkMessageBox import showerror

from penview import *
from model import *
from dialog import *

class PVController(Thread):
    
    def __init__(self, conf, window):
        Thread.__init__(self)
        self.conf = conf
        self.window = window

        self.loop = True
        self.action_q = Queue()

        window.set_controller(self)

    def q(self, action):
        self.action_q.put(action)

    def run(self):
        while self.loop:
            task = self.action_q.get()
            try:
                self.get_handler(task)()
            except Exception, e:
                print "Exception in PVController.run(): " + str(e)
                if debug_flag:
                    print_exc()
                else:
                    showerror(app_name, str(e))
            finally:
                self.action_q.task_done()

    def wait_idle(self):
        self.window.wait_idle()
        self.action_q.join()

    # all event handlers

    def do_quit_app(self):
        self.window.stop()
        self.stop()

    def do_show_graph(self):
        self.conf.set_viewmode(ViewMode.graph)

#    def do_show_table(self):
#        self.conf.set_viewmode(ViewMode.table)

    def do_open_exp(self):
        self._open(OpenWizard.get_ex_file())

    def do_import_exp(self):
        self._open(ImportWizard.get_ex_file())

    def _open(self, exp_file):
        self.conf.add_open_experiment(OpenExperiment(exp_file, self.window))

    def get_handler(self, action):
        try:
            return getattr(self, "do_" + pvaction_name[action])
        except AttributeError:
            raise Exception("Sorry, '%s' is not yet implemented" % pvaction_name[action])