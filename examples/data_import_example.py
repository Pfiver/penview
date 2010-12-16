#!/usr/bin/python
# encoding: utf-8

import os
from data_import import CSVImporter
from data_access import ExperimentFile
    
path = '.' + os.sep
filename = 'Abklingkonstante.csv'       
filename = 'Eigenfrequenz (Chaos2).csv' 
filename = 'Motorkalibrierung.csv'     
uri = path + filename
print "uri: %s" % uri
data = CSVImporter(uri)
print "values: %s" % data.values
print "metadata: %s" % data.metadata

#e = ExperimentFile(':memory:',3)
#e = ExperimentFile('abklingkonstante.sqlite')
#e = ExperimentFile('eigenfrequenz_chaos2.sqlite')
e = ExperimentFile('motorkalibrierung.sqlite',2)
e.store_values(1, data.values)
e.store_metadata(data.metadata)

result = e.load_values(1)
print "\nresult exp1:\n" + str(result)
print e.load_metadata()

e.close()