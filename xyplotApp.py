from Tkinter import *
from xyplot import *
    
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class XYPlotApp:
   def __init__(self, parent=0):
      self.mainWindow = Frame(parent)
      self.xyPlot=XYPlot(self.mainWindow,800,600)
      fButtons = Frame(self.mainWindow, border=2, relief="groove")
      bQuit = Button(fButtons, text="Quit",command=self.mainWindow.quit)
      bRectangle=Button(fButtons, text="Draw Rectangle",command=self.xyPlot.drawRectangle)
      bPlotData=Button(fButtons, text="Draw Data",command=self.xyPlot.plotSampleData)
      bQuit.pack(side="right")
      bRectangle.pack(side="right")
      bPlotData.pack(side="right")
      fButtons.pack(fill="both",expand="1")
      self.mainWindow.pack(fill="both",expand="1")

mainWindow=Tk()
app=XYPlotApp(mainWindow)
mainWindow.mainloop()

