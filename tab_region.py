from ttk import Notebook # ttk wrapper for TABS
from Tkinter import *

class TabRegion(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.notebook = Notebook(self)
        self.notebook.pack()
        self.notebook.add(Label(text="TabRegion"),text="Tab1")