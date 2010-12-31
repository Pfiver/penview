#!/usr/bin/python

from Tkinter import *
from threading import Thread

root = None
label = None
button = None

def run():
    global root, label, button
    root = Frame()
    root.bind("<Map>", printstuff)
    
    button = Button(root, text="Quit", command=root.quit)
    button.pack(side=BOTTOM)
    
    label = Label(root, text="Hello, world!")
    label.pack()

    scale = Scale(root)
    scale.pack()

    root.pack()
    root.mainloop()

def printstuff(event):
    for w in root, label, button:
        print w.pack_info()

Thread(target=run).start()

