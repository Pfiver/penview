#!/usr/bin/python
# encoding: utf-8

import os, re, csv

from penview import *

class CSVImporter:
    """import module for CSV files"""
    
    def __init__(self, uri):
        self.file = uri
        self.values = []
        self.metadata = {}
        self.rowsize = -1
        self._load_values()
        self._load_metadata()
 
    def _load_values(self):
        valuesReader = csv.reader(open(self.file), delimiter=',', quotechar='"')
        row = valuesReader.next()
        if not (row[0] == 't' and row[1] == 'v1'): # ignore the first row (we already know the title row)
            print "Erste Reihe entspricht nicht dem Standardformat"
        for row in valuesReader:
            if self.rowsize == -1:
                self.rowsize = len(row)
                for value in reversed(row): # test how wide the row is and ignore further values
                    if value == '':
                        self.rowsize -= 1
                    else:
                        break
            self.values += [row[:self.rowsize]]     # FIXME: if a row is empty, the empty string is inserted into values which results
                                                    # in the empty string being inserted into the database (DESPITE the column having type FLOAT !!!)
                                                    # I would therefore like empty strings to be convertet to "None" instead which would
                                                    # result in "null" beeing added to the database and converted back to "None" on access

    def _load_metadata(self):
        metadataReader = csv.reader(open(re.sub('\.csv$', '.metadata.csv', self.file)), delimiter=',', quotechar='"')
        row = metadataReader.next()
        if not (row[0] == 'name' and row[1] == 'value'): # ignore the first row (we already know the title row)
            print "meta: Erste Reihe entspricht nicht dem Standardformat"
        for row in metadataReader:
            if row[1] != '':
                self.metadata.update(((row[0], unicode(row[1], 'utf-8')),))
