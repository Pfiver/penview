from Tkinter import *

root = Tk()

# http://effbot.org/zone/tkinter-scrollbar-patterns.htm

#frame = Frame(root, bd=2, relief=SUNKEN)
frame = Frame(root)

frame.grid_rowconfigure(0, weight=1)
frame.grid_columnconfigure(0, weight=1)

xscrollbar = Scrollbar(frame, orient=HORIZONTAL)
xscrollbar.grid(row=1, column=0, sticky=E+W)

yscrollbar = Scrollbar(frame)
yscrollbar.grid(row=0, column=1, sticky=N+S)

canvas = Canvas(frame, scrollregion=(0, 0, 1000, 1000),
               xscrollcommand=xscrollbar.set,
               yscrollcommand=yscrollbar.set, width=1000, height=800)

canvas.grid(row=0, column=0, sticky=N+S+E+W)

class Object:
	pass
self = Object()

self.width, self.height = 1000, 1000
self.bgcolor = "white"
_color="blue"
canvas.create_rectangle(0, 0, self.width, self.height, fill=self.bgcolor)
canvas.create_line(0, self.height / 2, self.width, self.height / 2, width=2, fill=_color)
canvas.create_line(self.width / 2, 0, self.width / 2, self.height, width=2, fill=_color)

xscrollbar.config(command=canvas.xview)
yscrollbar.config(command=canvas.yview)

frame.pack()

root.mainloop()
