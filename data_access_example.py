#!/usr/bin/python
# encoding: utf-8

import sys
from data_access import Experiment

dbpath = '/tmp/' # for POSIX compatible Systems (e.g. MacOSX or Linux )
dbpath = 'C:\Temp' # for Windows (not tested)
dbname = 'example'
dbdestination = dbpath + dbname    

dbdestination = ':memory:' # Use :memory: for testing purposes, DB is lost after runtime ends

vn = 3 # Number of y-values (e.g. v1, v2, v3 -> vn = 3)

# create an instance of an experiment or a series of experiments
e = Experiment(dbdestination,vn) 

print "\nValues: "

# store your values here: Must look like this:
# [[ t, v1 , v2, v3 ]] or [( t, v1 , v2, v3 )]
# [[type(double), type(double), ...., ....]]
# or [(type(double), type(double), ...., ....)]
values = [[0.0, 23.0, 42.0, 13.37], [0.0, 42.1, 23.01, 73.31]]

# store your values of experiment 1
e.store_values(1, values)

# store your values of experiment 2
e.store_values(2, values)

# get only results from experiment 1
result = e.load_values(1)

print "\nresult exp1:\n" + str(result)

# get results from all experiments series
allresults = e.load_values()

print "\nall results:\n" + str(allresults)


print "\nMetadata: "

for metadata in ({"x":"y"}, {"x":"z"}, {"name":"x1", "v1unit":"m/s^2"}):
        e.store_metadata(metadata)
print e.load_metadata()

# close the database connection
e.close()

# delete Database if not it is a file on the filesystem
if dbdestination != ":memory:": os.unlink(dbdestination)   