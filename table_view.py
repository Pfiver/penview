# encoding: utf-8

from Tkinter import *

from recipe_52266 import MultiListbox

from penview import *

class PVTable(MultiListbox):

    def __init__(self, parent, window):
        debug("lots of work ahead here")
        self.parent = parent
        MultiListbox.__init__(self, self.parent, ("No Data",)) # Workaround for first call error: "AttributeError: PVTable instance has no attribute 'tk'"
#        conf.add_ox_listener(self.ox_update)
 
    def ox_update(self, conf):
        headers = ["Zeit",]
        data = []
        for ox in conf.open_experiments:
            # HEADER
            ox.header = self.get_header(ox)
            print "ox.header: %s" % ox.header
            for header in ox.header:
                headers.append(header)
            # DATA(s)
            print len(self.get_data(ox))
            for j in range(len(self.get_data(ox))):
#                print "self.get_data(ox)[%d]:" % j
#                print self.get_data(ox)[j]
                data.append(self.get_data(ox)[j])
#        print "calling update_table(headers, data): %s, %s" % (headers, data)
        self.update_table(headers, data)
        
    def get_header(self, ox):
        # Add Description (Table Header)
        header = []
        for i in range(ox.nvalues):
            header.append( ox.get_desc(i), )
        return header

    def get_data(self, ox):
        data = []
        self.cols = ox.nvalues # get the count of columns
        self.rows = len(ox.values[1]) # get the length of v1 values (v1 exists!)
        # Add Data from Experiment Table
        for row in range(self.rows):
#            print "ox.sqlvalues[%s]: %s " % ( row, ox.sqlvalues[row] )
            data.append(ox.sqlvalues[row],)
        return data
                
    def update_table(self, header, data):
        MultiListbox.__init__(self, self.parent, header)
#        print "data: %s" % data
        for row in range(len(data)):
#            print "row: %s " % row
            self.insert(END, data[row])
