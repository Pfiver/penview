#!/usr/bin/python
# encoding: utf-8

import os, sys

# debugging infrastructure
#
debug_flag = False

if not debug_flag:
    def debug(*args):
        pass
else:
    def debug(*args):
        if len(args) and type(args[0]) != str:
            args = " - ".join(str(arg) for arg in args)
        frame = sys._getframe(1); func = frame.f_code.co_name
        if 'self' in frame.f_locals: func = frame.f_locals['self'].__class__.__name__ + "." + func
        print "(%s:%d) in %s(): %s" % (os.path.basename(frame.f_code.co_filename), frame.f_lineno, func, args[0] % args[1:])

# this script is in penview/scripts OOoLib is stored in penview/lib - adjust the module import search path
#
sys.path.append(os.path.join(os.path.dirname(sys._getframe().f_code.co_filename), "../lib"))

import shlex, subprocess
cmdinput = "/usr/bin/soffice -accept=socket,host=localhost,port=8100;urp"
debug("cmdinput %s" % cmdinput)
args = shlex.split(cmdinput)
try:
    office = subprocess.Popen(args)
    office.wait()
    debug("OO is running")
except:
    raise Exception("OpenOffice not installed or running on non-POSIX Operating System")

from OOoLib import *

def Excel2CSV(path):
    dir = os.path.dirname(path) + os.sep
    debug("dir: %s" % dir)
    filename = os.path.basename(path)
    debug("filename: %s" % filename)
    filebase = ".".join(filename.split('.')[:-1])
    debug("filebase: %s" % filebase)

###################### Save Messdaten Sheet in CSV #####################
    cFile = dir + filename # Linux 
    debug("cFile: %s" % cFile)
    cURL = convertToURL( cFile ) 
    debug("cURL: %s" % cURL)
    oDoc = StarDesktop.loadComponentFromURL( cURL, "_blank", 0, Array() ) 
    debug("oDoc: %s" % oDoc)

    oDoc.getSheets().removeByName( "Metadaten" )    
    # Here are two ways to get access to one of the various sheets 
    #  in the spreadsheet document. 
    # Note that these don't make the sheet *vislble*, they merely give 
    #  access to the sheet's content within the program. 
#    oSheet = oDoc.getSheets().getByIndex( 0 ) # get the zero'th sheet 
    oSheet = oDoc.getSheets().getByName( "Messdaten" ) # get by name 
    debug("oSheet: %s" % oSheet)
    
    # Prepare the filename to save. 
    # We're going to save the file in several different formats, 
    #  but all based on the same filename. 
    #cFile = "C:\Documents and Settings\dbrewer\Desktop\MyCalc" # Windows 
#    cFile = "/home/archon/Desktop/Marc Patrick/Potentialtopf (Chaos1).xls" # Linux 
    
    # Now save it in CSV format. 
    cURL = convertToURL( dir + "csv/" + filebase + ".csv" ) 
    debug("cURL: %s" % cURL)
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "Text - txt - csv (StarCalc)" ) ) ) 
    debug("oDoc: %s" % oDoc)
    # Now close the document 
    oDoc.close( True )
 
###################### Save Metadaten Sheet in CSV #####################
    
    cFile = dir + filename # Linux 
    debug("cFile: %s" % cFile)
    cURL = convertToURL( cFile ) 
    debug("cURL: %s" % cURL)
    oDoc = StarDesktop.loadComponentFromURL( cURL, "_blank", 0, Array() ) 
    debug("oDoc: %s" % oDoc)
    
    oDoc.getSheets().removeByName( "Messdaten" )   
    oSheet = oDoc.getSheets().getByName( "Metadaten" ) # get by name 
    debug("oSheet: %s" % oSheet)
    cURL = convertToURL( dir + "csv/meta"+ filebase + ".csv" )
    debug("cURL: %s" % cURL)
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "Text - txt - csv (StarCalc)" ) ) ) 
    debug("oDoc: %s" % oDoc)

    # Now close the document 
    oDoc.close( True )

dirpath = "/home/archon/Desktop/Marc Patrick/"
#dirpath = "/invalid"

inputfiles = []

#files = os.listdir(path)
try:
#    arg = sys.argv[1:]
    arg = dirpath
    debug("arg: %s" % arg)
    # traverse folder from dirpath
    files = os.listdir(arg)
except:
    print "No valid Argument, I need an existing dir"
    office.wait()
    office.terminate()

# filter out all non-xls Files
for file in files:
    try:
        if file.split('.')[-1] == "xls":
            inputfiles.append(file)
    except:
        pass
debug("inputfiles: %s" % inputfiles)

# convert every xls File into 2 individual csv 
# (Messdaten -> filename, Metadaten -> metafilename)
for file in inputfiles:
    filepath = os.path.dirname(arg) + os.sep + file
    try:
        debug("filepath %s" % filepath)
        Excel2CSV(filepath)
    except:
        raise Exception("No such file: %s" % filepath)

# has already forked
#office.terminate()
