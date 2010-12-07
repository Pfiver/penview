from Tkinter import *
from random import *

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class XYPlot:
  """ """
  def __init__(self,_parent,_width,_height):
    self.width=_width
    self.height=_height
    self.parent=_parent
    self.bgcolor="#EEEEEE"
    self.fgcolor="black"
    self.drawcolor="blue"
    self.canvas = Canvas(self.parent,width=self.width,height=self.height,bg=self.bgcolor)
    self.repaint(self.fgcolor)
    self.canvas.pack(fill="both", expand="1")
    self.canvas.bind('<Configure>',self.resize)
    
  def repaint(self,_color):
    self.canvas.create_rectangle(0,0, self.width, self.height,fill=self.bgcolor)
    self.canvas.create_line(0,self.height/2,self.width,self.height/2,width=2,fill=_color)
    self.canvas.create_line(self.width/2,0,self.width/2,self.height,width=2,fill=_color)

  def resize(self,event ):
    self.repaint(self.bgcolor)
    self.width=event.width-6
    self.height=event.height-6
    self.canvas.configure(width=self.width,height=self.height)
    self.repaint(self.fgcolor)

  def drawRectangle(self):
    self.repaint(self.fgcolor)
    self.canvas.create_rectangle(self.width/2-self.width/10,self.height/2-self.height/10, self.width/2+self.width/10, self.height/2+self.height/10,fill=self.drawcolor)
    
  def plotSampleData(self):
    data=[]
    for i in range(0,self.width,self.width/50):
  	  data.append(i)
  	  data.append(self.height-(randint(0,self.height)))
    self.repaint(self.fgcolor)
    self.canvas.create_line(data,fill=self.drawcolor)


