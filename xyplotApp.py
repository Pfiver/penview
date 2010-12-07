from Tkinter import *
from xyplot import *

class XYPlotApp:
   def __init__(self):

      self.mainWindow = Frame()

      self.xyPlot = XYPlot(self.mainWindow, 800, 600)

      Buttons = Frame(self.mainWindow, border=2, relief="groove")

      Quit = Button(Buttons, text="Quit", command=self.mainWindow.quit)
      PlotData = Button(Buttons, text="Draw Data", command=self.xyPlot.plotSampleData)
      Rectangle = Button(Buttons, text="Draw Rectangle", command=self.xyPlot.drawRectangle)

      Quit.pack(side="right")
      Rectangle.pack(side="right")
      PlotData.pack(side="right")

      self.xyPlot.pack(fill="both", expand="1")
      Buttons.pack(fill="both", expand="1")
      self.mainWindow.pack(fill="both", expand="1")

tk = Tk()
app = XYPlotApp()
tk.mainloop()
