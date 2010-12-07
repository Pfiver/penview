from random import *
from Tkinter import *

# The "view"
class PenViewUI:
    def __init__(self):

        # level 0 widget
        self.window = Frame() # main-window (= top-level container)
                              # seems a (confusing) Tk() call is not (any more) needed 

        # level 1 widgets
        self.xy_plot = XYPlot(self.window, 800, 600) # custom canvas widget
        self.buttons = Frame(self.window, border=2, relief="groove") # button container

        # level 2 widgets
        Quit = Button(self.buttons, text="Quit", command=self.window.quit)
        PlotData = Button(self.buttons, text="Draw Data", command=self.xy_plot.plot_random_data)
        Rectangle = Button(self.buttons, text="Draw Rectangle", command=self.xy_plot.draw_rectangle)

        # pack level 2 widgets
        for btn in Quit, Rectangle, PlotData:
            btn.pack(side=RIGHT)

        # pack level 1 widgets
        for frm in self.xy_plot, self.buttons:
            frm.pack(fill=BOTH, expand=1)

        # bind our map handler
        self.xy_plot.bind("<Map>", self.map_handler)
        
        # This last pack() sort of maps the top-level frame into the toplevel
        # window that was implicitly created during the first Frame object creation.
        # Compulsory, but I'm not *really* sure how this fits into the whole Tkinter logic.
        self.window.pack()

    def handle_events(self):
        self.window.mainloop()

    def map_handler(self, event):
        pass
        # Here we'd have to check the original height of the
        # top-level frame and subtract the height of the xy_plot
        # to find out how much space the buttons take up
        # - but we use scrollbars now anyway and don't resize the xy_plot canvas on window resize
#        print event.widget.__class__
#        print "w: %d" % self.window.winfo_width()
#        print "W: %d" % self.xy_plot.winfo_width()
#        print "h: %d" % self.window.winfo_height()
#        print "H: %d" % self.xy_plot.winfo_height()

class PlotRegion(Frame):
    pass

# a custom canvas to display xy-plots
class XYPlot(Canvas):
    """
    """
    def __init__(self, _parent, _width, _height):
        self.parent = _parent
        self.width, self.height = _width, _height

        self.fgcolor = "black"
        self.bgcolor = "#EEEEEE"
        Canvas.__init__(self, self.parent, bg=self.bgcolor,
                              width=self.width, height=self.height)

        self.draw_axes(self.fgcolor)
        self.bind('<Configure>', self.resize_handler)

    def draw_axes(self, _color="black"):
        self.create_rectangle(0, 0, self.width, self.height, fill=self.bgcolor)
        self.create_line(0, self.height / 2, self.width, self.height / 2, width=2, fill=_color)
        self.create_line(self.width / 2, 0, self.width / 2, self.height, width=2, fill=_color)

    def draw_rectangle(self):
        self.draw_axes()
        self.create_rectangle(self.width / 2 - self.width / 10,
                              self.height / 2 - self.height / 10,
                              self.width / 2 + self.width / 10,
                              self.height / 2 + self.height / 10, fill="blue")

    def plot_random_data(self):
        self.draw_axes()
        data = []
        for i in range(0, self.width, self.width / 50):
            data.append(i)
            data.append(self.height - (randint(0, self.height)))
        self.create_line(data, fill=self.drawcolor)

    def resize_handler(self, event):
        pass
#        print "w: %d" % self.winfo_width()
#        print "W: %d" % self.parent.winfo_width()
#        print "h: %d" % self.winfo_height()
#        print "H: %d" % self.parent.winfo_height()
#        self.repaint(self.bgcolor)
#        self.width = event.width
#        self.height = event.height
#        self.canvas.configure(width=self.width, height=self.height)
#        self.repaint(self.fgcolor)
