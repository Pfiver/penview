# from http://code.activestate.com/recipes/52266/

from Tkinter import *

class MultiListbox(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        # One List
        self.lists = [MiltiListbox.List(self, "No Data\n")]
    
        # The Scrollbar
        frame = Frame(self)
        frame.pack(side=RIGHT, fill=Y)
        Label(frame, text="\n", borderwidth=1).pack(fill=X)
        sb = Scrollbar(frame, orient=VERTICAL, command=self._scroll)
        sb.pack(expand=YES, fill=Y)

#    da wir die table columns wiederverwenden wollen aber die experiment id's immutable sein sollen,
#    es gibt ein experiment.id zu table.column mapping

        self.table_columns = []

        for l in self.lists:
            l['yscrollcommand']=lambda *args: self._yscroll(sb, *args)

    class List(Frame):
        def __init__(self, parent, header):
            Frame.__init__(self, parent)
            self.pack(side=LEFT, expand=YES, fill=BOTH)
            lb = Label(self, text=header)
            lb.pack(fill=X)
            lb = Listbox(self, borderwidth=0, selectborderwidth=0, exportselection=FALSE)
            lb.pack(expand=YES, fill=BOTH)

            lb.bind('<B2-Motion>', lambda e: parent._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e: parent._button2(e.x, e.y))
            lb.bind('<B1-Motion>', lambda e: parent._select(e.y))
            lb.bind('<Button-1>', lambda e: parent._select(e.y))
            lb.bind('<Leave>', lambda e: 'break')

            self.lb = lb

    def add_list(self, list, group, nr):
        if len(self.groups) < group:
            self.groups[group] = Frame(self)
            self.groups[group].grid(column=group)

        if nr not in self.table_columns:
            self.table_columns[nr] = self.ncolumns

reduce(lambda lo, hi: hi < 5 and hi or lo, range(10))
        self.lists[(group, self.table_columns[nr])] = list

    def show(self, group, nr):
        self.lists[(group, column)].grid_forget()
        
    def hide(self, group, nr):
        for group, column in self.lists:
            if nr == 
        self.lists[(group, column)].grid(column=column)

    def _select(self, y):
    	row = self.lists[0].nearest(y)
    	self.selection_clear(0, END)
    	self.selection_set(row)
    	return 'break'

    def _button2(self, x, y):
    	for l in self.lists: l.scan_mark(x, y)
    	return 'break'

    def _b2motion(self, x, y):
    	for l in self.lists: l.scan_dragto(x, y)
    	return 'break'

    def _scroll(self, *args):
    	for l in self.lists:
    	    apply(l.yview, args)

    def _yscroll(self, sb, top, bottom):
        for l in self.lists:          # FIXME: the event generating listbox is also scrolled again.... seems to work so far
            l.yview('moveto', top)
        sb.set(top, bottom)

    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
    	for l in self.lists:
    	    l.delete(first, last)

    def get(self, first, last=None):
    	result = []
    	for l in self.lists:
    	    result.append(l.get(first,last))
    	if last: return apply(map, [None] + result)
    	return result
	    
    def index(self, index):
        self.lists[0].index(index)

    def insert(self, index, *elements):
    	for e in elements:
    	    i = 0
    	    for l in self.lists:
    		l.insert(index, e[i])
    		i = i + 1

    def size(self):
        return self.lists[0].size()

    def see(self, index):
    	for l in self.lists:
    	    l.see(index)

    def selection_anchor(self, index):
    	for l in self.lists:
    	    l.selection_anchor(index)

    def selection_clear(self, first, last=None):
    	for l in self.lists:
    	    l.selection_clear(first, last)

    def selection_includes(self, index):
	   return self.lists[0].selection_includes(index)

    def selection_set(self, first, last=None):
    	for l in self.lists:
    	    l.selection_set(first, last)

if __name__ == '__main__':
    tk = Tk()
    mlb = MultiListbox(tk)
    for i, header in enumerate("List 1\nfoo", "List 2\nbar")
        data = []
        for j in range(1000):
            data.append("List %d Row %d" % (i + 1, j) for j in range(1000)
        mlb.add_list(header, data)
    mlb.pack(expand=YES,fill=BOTH)
    tk.mainloop()
