import os
from data_import import CSVImporter
from data_access import ExperimentFile
    
path = '.' + os.sep
filename = 'Abklingkonstante.csv'            
uri = path + filename
data = CSVImporter(uri)
print "values: %s" % data.values
print "metadata: %s" % data.metadata

e = ExperimentFile(':memory:')
e.store_values(1, data.values)
e.store_metadata(data.metadata)

result = e.load_values(1)
print "\nresult exp1:\n" + str(result)
print e.load_metadata()

e.close()