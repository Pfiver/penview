# encoding: utf-8

from Tkinter import *

from penview import *
from graph_view import *
from table_view import *

class DataRegion(Frame):
    def __init__(self, parent, window):
        Frame.__init__(self, parent)

        self.window = window

        # set up the graph view, consisting of a controls and a scrollable plot region
        #
        self.controls_region = PlotControls(self, window)
        self.plot_region = ScrollRegion(self)

        self.xy_plot = XYPlot(self.plot_region, window, 800, 600)
        self.xy_plot.pack(fill=BOTH, expand=1)

        self.plot_region.scroll_child(self.xy_plot)

        # set up the table view
        #
        self.table_region = PVTable(self, window)

        # make sure we know when to switch
        #
        window.conf.add_viewmode_listener(self.viewmode_update)

    def show_table(self):
        self.plot_region.pack_forget()          # FIXME: on the first call the widgets are actually not yet packed
        self.controls_region.pack_forget()

        self.table_region.pack(fill=BOTH, expand=YES)

    def show_plot(self):
        self.table_region.pack_forget()          # FIXME: on the first call the widget is actually not yet packed

        # URK - use the pack-widgets-that-should-stay-visible-on-window-resize-first hack here
        # i.e.: don't change the pack()ing order !
        #
        self.controls_region.pack(side=BOTTOM, fill=X, expand=0)
        self.plot_region.pack(fill=BOTH, expand=1)

    def viewmode_update(self, conf):
        if conf.viewmode == ViewMode.graph:
            self.show_plot()
        elif conf.viewmode == ViewMode.table:
            self.show_table()
            raise Exception("Table view mode is not yet working very well....")
