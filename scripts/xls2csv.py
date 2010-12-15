from OOoLib import *
import os
import sys

def CalcExample(path):
    dir = os.path.dirname(path) + os.sep
    print dir
    filename = os.path.basename(path)
    print filename
    filebase = substr(filename,".xls")

###################### Save Messdaten Sheet in CSV #####################
    cFile = dir + filename # Linux 
    print "cFile: %s" % cFile
    cURL = convertToURL( cFile ) 
    print "cURL: %s" % cURL
    oDoc = StarDesktop.loadComponentFromURL( cURL, "_blank", 0, Array() ) 
    print "oDoc: %s" % oDoc

    oDoc.getSheets().removeByName( "Metadaten" )    
    # Here are two ways to get access to one of the various sheets 
    #  in the spreadsheet document. 
    # Note that these don't make the sheet *vislble*, they merely give 
    #  access to the sheet's content within the program. 
#    oSheet = oDoc.getSheets().getByIndex( 0 ) # get the zero'th sheet 
    oSheet = oDoc.getSheets().getByName( "Messdaten" ) # get by name 
    print "oSheet: %s" % oSheet
    
    # Prepare the filename to save. 
    # We're going to save the file in several different formats, 
    #  but all based on the same filename. 
    #cFile = "C:\Documents and Settings\dbrewer\Desktop\MyCalc" # Windows 
#    cFile = "/home/archon/Desktop/Marc Patrick/Potentialtopf (Chaos1).xls" # Linux 
    
    # Now save it in CSV format. 
    cURL = convertToURL( dir + "csv/" + filename + ".csv" ) 
    print "cURL: %s" % cURL
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "Text - txt - csv (StarCalc)" ) ) ) 
    print "oDoc: %s" % oDoc
    # Now close the document 
    oDoc.close( True )
 
###################### Save Metadaten Sheet in CSV #####################
    
    cFile = dir + filename # Linux 
    print "cFile: %s" % cFile
    cURL = convertToURL( cFile + ".xls" ) 
    print "cURL: %s" % cURL
    oDoc = StarDesktop.loadComponentFromURL( cURL, "_blank", 0, Array() ) 
    print "oDoc: %s" % oDoc
    
    oDoc.getSheets().removeByName( "Messdaten" )   
    oSheet = oDoc.getSheets().getByName( "Metadaten" ) # get by name 
    print "oSheet: %s" % oSheet
    cURL = convertToURL( dir + "csv/meta"+ filename + ".csv" )
    print "cURL: %s" % cURL 
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "Text - txt - csv (StarCalc)" ) ) ) 
    print "oDoc: %s" % oDoc

    # Now close the document 
    oDoc.close( True )

for f in sys.argv[1:]:
    print f
    try:
        print "Arguments: %s \n" % sys.argv[f]
        CalcExample(f)
    except Exception:
        print "FileError for %s" % f
    