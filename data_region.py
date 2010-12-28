# encoding: utf-8

from Tkinter import *

from penview import *
from graph_view import *
from table_view import *

class DataRegion(Frame):
    def __init__(self, parent, window):
        Frame.__init__(self, parent)

        self.window = window

        self.controls_region = PlotControls(self, window)
        self.plot_region = ScrollRegion(self)

        self.xy_plot = XYPlot(self.plot_region, window, 800, 600)
        self.xy_plot.pack(fill=BOTH, expand=1)

        self.plot_region.scroll_cild(self.xy_plot)

#        self.table_region = PVTable(self, self.conf)

        window.conf.add_viewmode_listener(self.viewmode_update)

    def show_table(self):
        self.plot_region.pack_forget()          # FIXME: on the first call the widgets are not yet packed
        self.controls_region.pack_forget()

        self.table_region.pack(fill=BOTH, expand=YES)

    def show_plot(self):
#        self.table_region.pack_forget()          # FIXME: on the first call the widget is not yet packed

        # urk - use the pack-regions-that-should-stay-visible-on-window-resize-first hack
        self.controls_region.pack(side=BOTTOM, fill=X, expand=0)
        self.plot_region.pack(fill=BOTH, expand=1)

    def viewmode_update(self, conf):
        if conf.viewmode == ViewMode.graph:
            self.show_plot()
        elif conf.viewmode == ViewMode.table:
            self.show_table()
