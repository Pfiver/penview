#!/usr/bin/python
# encoding: utf-8
# vim:sw=4

import os, sys

# comment out if you don't need
#autoargs = ( "/home/archon/Desktop/Marc Patrick/", )

# debugging infrastructure
#
debug_flag = False

import shlex, subprocess
def start_ooo():
    cmd = "/usr/bin/soffice -headless -accept=socket,host=localhost,port=8100;urp"
    debug("cmdinput %s" % cmd)
    args = shlex.split(cmd)
    try:
	office = subprocess.Popen(args)
	office.wait()
	debug("OO running")
    except:
	raise Exception("OpenOffice not installed or running on non-POSIX Operating System")

    for n in range(5):
	try:
	    import OOoLib
	    break
	except:
	    debug("wait just a second....")
	    from time import sleep
	    sleep(1)
    if not 'OOoLib' in locals():
	raise Exception("couldn't import OOoLib")


import re
def xls2csv(infile):
    oDoc = StarDesktop.loadComponentFromURL(convertToURL(os.path.abspath(infile)), "_blank", 0, Array())
    outbase = os.path.basename(infile).rpartition(".")[0]

    outfile = outbase + '.csv'
    oSheet = oDoc.getSheets().getByName("Messdaten")
    oDoc.getCurrentController().setActiveSheet(oSheet)
    oDoc.storeToURL(convertToURL(os.path.abspath(outfile)), Array(makePropertyValue("FilterName", "Text - txt - csv (StarCalc)")))
    print "wrote " + outfile
    
    outfile = outbase + '.metadata.csv'
    oSheet = oDoc.getSheets().getByName("Metadaten")
    oDoc.getCurrentController().setActiveSheet(oSheet)
    oDoc.storeToURL(convertToURL(os.path.abspath(outfile)), Array(makePropertyValue("FilterName", "Text - txt - csv (StarCalc)"),
								  makePropertyValue("FilterOptions", '44,34,utf-8')))	# options: sep,delim,encoding
    print "wrote " + outfile
 
    oDoc.close(True)

if __name__ == "__main__":

    from utils import *

    files = fileargs("xls")
    if not len(files):
	print "usage: %s cvs-files"
	print
	print "	converts the given xls files to csv - generated files are stored in the current directory"
	sys.exit(0)

    start_ooo()
    from OOoLib import *

    map(xls2csv, files)

    StarDesktop.terminate()
