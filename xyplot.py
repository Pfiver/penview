from Tkinter import *
from random import *


class XYPlot(Canvas):
    """
    """
    def __init__(self, _parent, _width, _height):
        self.width = _width
        self.height = _height
        self.parent = _parent

        self.bgcolor = "#EEEEEE"
        self.fgcolor = "black"
        self.drawcolor = "blue"

        Canvas.__init__(self, self.parent, bg=self.bgcolor,
                              width=self.width, height=self.height)

        self.repaint(self.fgcolor)
        self.bind('<Configure>', self.resize)

    def repaint(self, _color):
        self.create_rectangle(0, 0, self.width, self.height, fill=self.bgcolor)
        self.create_line(0, self.height / 2, self.width, self.height / 2, width=2, fill=_color)
        self.create_line(self.width / 2, 0, self.width / 2, self.height, width=2, fill=_color)

    def resize(self, event):
        print "w: %d" % self.winfo_width()
        print "W: %d" % self.parent.winfo_width()
        print "h: %d" % self.winfo_height()
        print "H: %d" % self.parent.winfo_height()
#        self.repaint(self.bgcolor)
#        self.width = event.width
#        self.height = event.height
#        self.canvas.configure(width=self.width, height=self.height)
#        self.repaint(self.fgcolor)

    def drawRectangle(self):
        self.repaint(self.fgcolor)
        self.create_rectangle(self.width / 2 - self.width / 10, self.height / 2 - self.height / 10, self.width / 2 + self.width / 10, self.height / 2 + self.height / 10, fill=self.drawcolor)

    def plotSampleData(self):
        data = []
        for i in range(0, self.width, self.width / 50):
            data.append(i)
            data.append(self.height - (randint(0, self.height)))
        self.repaint(self.fgcolor)
        self.create_line(data, fill=self.drawcolor)


