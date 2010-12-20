from Queue import Queue
from threading import Thread

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
            if debug_flag:
                self.get_handler(a)()
            else:
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
        
    def reset_upd(self):

        experiments = self.conf.open_experiments
    
        cols = experiments[0].get_nvalues() + 1
        
        max_values = {}
        min_values = {}
        for i in range(cols):
            imax = None
            imin = None
            for j in range(len(experiments)):
                jmax = max(experiments[j].values[i])
                jmin = min(experiments[j].values[i])
                if not imax or jmax > imax:
                    imax = jmax
                if not imin or jmin < imin:
                    imin = jmin
            max_values[i] = imax
            min_values[i] = imin

        ranges = [max_values[i] - min_values[i] for i in range(cols)]
        
        ppd = self.ui.data_region.xy_plot.ppd
        win_width = self.ui.data_region.xy_plot.width
        win_height = self.ui.data_region.xy_plot.height

        self.conf.values_upd[0] = win_width / ppd * ranges[0]

        for i in range(1, cols):
            self.conf.values_upd[i] = win_height / ppd * ranges[i]

    def do_show_table(self):
        self.conf.set_view(PVTable)
        
    def do_show_graph(self):
        self.conf.set_view(XYPlot)