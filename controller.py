# encoding: utf-8

import os
from Queue import Queue
from threading import Thread
from traceback import print_exc
from tkMessageBox import showinfo, showerror

from penview import *
from model import *
from dialog import *

class PVController(Thread):

    # constructor & api methods
    #
    def __init__(self, conf, window):
        Thread.__init__(self)
        self.conf = conf
        self.window = window

        self.loop = True
        self.action_q = Queue()

        window.set_controller(self)

    def q(self, action):
        self.action_q.put(action)

    def wait_idle(self):
        self.window.wait_idle()
        self.action_q.join()

    def stop(self):
        self.loop = False

    # target function called by Thread.start()
    #
    def run(self):
        while self.loop:
            task = self.action_q.get()
            try:
                self.get_handler(task)()
            except Exception, e:
                if debug_flag:
                    print_exc()
                else:
                    self.window.tk_do(showerror, app_name, str(e))
            finally:
                self.action_q.task_done()

    # helper function
    #
    def get_handler(self, action):
        try:
            return getattr(self, "do_" + PVAction.name(action))
        except AttributeError:
            raise Exception("'%s' is not implemented yet" % PVAction.name(action))

    # event handlers for most defined actions
    #
    def do_quit_app(self):
        self.window.stop()
        self.stop()

    def do_show_graph(self):
        self.conf.set_viewmode(ViewMode.graph)

    def do_show_table(self):
        self.conf.set_viewmode(ViewMode.table)

    def do_show_about(self):
        self.window.tk_do(showinfo, "%s" % app_name, "Version %s" % app_version)

    def do_show_help(self):
        import webbrowser
        homepage = "http://p2000.github.com/penview/"
        message = """Your default web browser should take you to the PenView home page, %s, shortly.\n""" % homepage + \
                  """Check the "Documentation" section there and if you still need further help, please don't hesitate to write an email to the developpers."""
        webbrowser.open(homepage)
        self.window.tk_do(showinfo, "%s" % app_name, message)

    def do_open_exp(self):
        path = self.window.tk_do(Dialog.get_ex_path)
        if not path:
            return
        self.conf.add_open_experiment(OpenExperiment(ExperimentFile(path), self.window))

    def do_import_exp(self):
        path = self.window.tk_do(Dialog.get_csv_path)
        if not path:
            return
        csv = CSVImporter(path)
        while True:
            ex_path = self.window.tk_do(Dialog.get_ex_path)
            if not ex_path:
                return
            if not os.path.exists(ex_path):
                break
            if self.window.tk_do(askokcancel, "Experiment File", "File exists. Overwrite?"):
                os.unlink(ex_path)
                break

        if not ex_path.endswith(".sqlite"):
            ex_path += ".sqlite"

        ex_file = ExperimentFile(ex_path, csv.rowsize - 1)
        
        ex_file.store_values(1, csv.values)
        ex_file.store_metadata(csv.metadata)
        
        self.conf.add_open_experiment(OpenExperiment(ex_file, self.window))
        
    def do_reset_scale(self):
        plot = self.window.data_region.xy_plot
        self.conf.reset_upd(plot.ppd, plot.width, plot.height)

