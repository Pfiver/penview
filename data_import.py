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
        # create a csv-reader instance for the values file
        valuesReader = csv.reader(open(self.file), delimiter=',', quotechar='"')
        row = valuesReader.next()                       # get the first row
        if not (row[0] == 't' and row[1] == 'v1'):      # is it properly formatted ?
            print "Erste Reihe entspricht nicht dem Standardformat"
        for row in valuesReader:                        # for each data row
            if self.rowsize == -1:                      # is the row size already known ?
                for i in range(len(row), 0, -1):        # loop over the elements from the righthand side
                    if row[i-1]:                        # find the rightmost nonempty value
                        self.rowsize = i                # the rowsize is it's position+1
                        break                           # rowsize defined - done
            # If a column is empty, we convert it from "''" (empty string) to "None", to make the database contain
            # "null" instead of "''", which will be converted back to "None" by subsequent select statements.
            # Although the column type is FLOAT in the SQLite schema, the data will still be "''" (empty string)
            # because SQLite has no strict typing.
            self.values += [map(lambda v: v if v else None, row[:self.rowsize])]

    def _load_metadata(self):
        # derive the name of the metadata file from the name of the values file using the regular expression module
        md_file = re.sub('\.csv$', '.metadata.csv', self.file) 
        # create a csv-reader instance for the metadata file
        metadataReader = csv.reader(open(md_file), delimiter=',', quotechar='"')
        row = metadataReader.next()                         # get the first row
        if not (row[0] == 'name' and row[1] == 'value'):    # is it properly formatted ?
            print "CSVImporter._load_vaues(): warnung: Erste Reihe entspricht nicht dem Standardformat"
        for row in metadataReader:
            self.metadata.update(((row[0], unicode(row[1], 'utf-8')),))