from Tkinter import *
from threading import Thread
class UI(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.f=Frame()
	def run(self):
		self.f.mainloop()

ui=UI()
ui.start()
