#!/usr/bin/python
# encoding: utf-8

import os

from utils import *

from data_import import CSVImporter
from data_access import ExperimentFile

for infile in fileargs("csv"):
    data = CSVImporter(infile)

    outfile = os.path.basename(infile).rpartition(".")[0] + ".sqlite"

    if os.path.exists(outfile): os.unlink(outfile)

    e = ExperimentFile(outfile, data.rowsize - 1)

    e.store_values(1, data.values)
    e.store_metadata(data.metadata)

    e.close()

    print "wrote " + outfile
