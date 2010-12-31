#!/usr/bin/python
# encoding: utf-8

import os
import utils
from data_import import CSVImporter
from data_access import ExperimentFile
    
path = 'examples' + os.sep
#filename = 'Abklingkonstante.csv'       
filename = 'Motorkalibrierung.csv'     
#filename = 'Eigenfrequenz (Chaos2).csv' 

uri = path + filename
data = CSVImporter(uri)

e = ExperimentFile(':memory:', data.rowsize - 1)
#e = ExperimentFile('abklingkonstante.sqlite')
#e = ExperimentFile('motorkalibrierung.sqlite',2)
#e = ExperimentFile('eigenfrequenz_chaos2.sqlite')
e.store_values(1, data.values)
e.store_metadata(data.metadata)

print "imported vals:"
print data.values
print "imported meta:"
print data.metadata
print "stored vals:"
print e.load_values()
print "stored meta:"
print e.load_metadata()

e.close()
