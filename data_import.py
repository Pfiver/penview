#!/usr/bin/python
# encoding: utf-8

import os, csv

from penview import *

class Excel2CSV:
    pass
 
class CSVImporter:
    """import module for CSV files"""
    
    def __init__(self, uri):
        self.filename = os.path.basename(uri)
        self.path = os.path.dirname(uri)
        self.file = uri
        self.values = []
        self.metadata = {}
        self.values = self.load_values()
        self.metadata = self.load_metadata()
 
    def load_values(self):
        valuesReader = csv.reader(open(self.file, 'rb'), delimiter=',', quotechar='"')
        row = valuesReader.next()
        if not (row[0] == u't' and row[1] == u'v1'): # ignore the first row (we already know the title row)
            debug( "Erste Reihe entspricht nicht dem Standardformat" )
        rowsize = -1
        for row in valuesReader:
            if rowsize == -1:
                rowsize = len(row)
                for value in reversed(row): # test how big the row is and ignore further values
                    if value == '':
                        rowsize -= 1
                    else:
                        break
            self.values += [row[:rowsize]]     
        self.rowsize = rowsize
        #print "rowsize: %s" % rowsize
        #print "resized row: %s" % row[:rowsize] 
        return self.values      

    def load_metadata(self):
        metadataReader = csv.reader(open(self.path + "/" + "meta" + self.filename, 'rb'), delimiter=',', quotechar='"')
        row = metadataReader.next()
        debug("row: %s" % row)
        if not (row[0] == u'name' and row[1] == u'value'): # ignore the first row (we already know the title row)
            debug("meta: Erste Reihe entspricht nicht dem Standardformat")
        for row in metadataReader:
            if row[1] != '':
                self.metadata.update(dict(((row[0],unicode(row[1], 'utf-8')),)))
        return self.metadata