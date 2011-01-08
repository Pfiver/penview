# encoding: utf-8

from Tkinter import *

from recipe_52266 import MultiListbox

from penview import *

class PVTable(Frame):

    def __init__(self, parent, window):
        Frame.__init__(self, parent)

        self.window = window

        self.mlb = MultiListbox(self, ("\n",))
        
        window.conf.add_ox_listener(window.tk_cb(self.ox_update))
 
        debug("lots of work ahead here")

    def ox_update(self, conf):
        
        self.mlb.pack_forget()

        headers = []

        for i in range(conf.nvalues + 1):
            for ox in conf.open_experiments:
                if i <= ox.nvalues:
                    headers.append("%s %d\n(%s)" % (ox.get_desc(i), ox.id, ox.get_units(i)))

        self.mlb = MultiListbox(self, headers)

        row = 0
        while True:
            data = []
            for i in range(conf.nvalues + 1):
                for ox in conf.open_experiments:
                    if i <= ox.nvalues and row < len(ox.values[i]):
                        data.append(ox.values[i][row])
                    else:
                        data.append("")
            if not filter(lambda x: x != "", data):
                break
            self.mlb.insert(END, data)
            row +=1
    
        self.mlb.pack(expand=YES, fill=BOTH)
