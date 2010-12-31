from Danny.OOo.OOoLib import * 

def CalcExample(): 
    # create a new Calc spreadsheet. 
    oDoc = StarDesktop.loadComponentFromURL( "private:factory/scalc", "_blank", 0, Array() ) 
    #----- 
    # Use this instead to open an EXISTING calc document, 
    #  and assign it to variable oDoc. 
    #  cFile = "C:\Documents and Settings\danny\Desktop\MyCalc" # Windows 
    #  cFile = "/home/danny/Desktop/MyCalc.sxc" # Linux 
    #  cURL = convertToURL( cFile + ".sxc" ) 
    #  oDoc = StarDesktop.loadComponentFromURL( cURL, "_blank", 0, Array() ) 
    #----- 

    # Here are two ways to get access to one of the various sheets 
    #  in the spreadsheet document. 
    # Note that these don't make the sheet *vislble*, they merely give 
    #  access to the sheet's content within the program. 
    oSheet = oDoc.getSheets().getByIndex( 0 ) # get the zero'th sheet 
    #oSheet = oDoc.getSheets().getByName( "Sheet3" ) # get by name 
    
    #----- 
    # Put some sales figures onto the sheet. 
    oSheet.getCellByPosition( 0, 0 ).setString( "Month" ) 
    oSheet.getCellByPosition( 1, 0 ).setString( "Sales" ) 
    oSheet.getCellByPosition( 2, 0 ).setString( "End Date" ) 

    oSheet.getCellByPosition( 0, 1 ).setString( "Jan" ) 
    oSheet.getCellByPosition( 0, 2 ).setString( "Feb" ) 
    oSheet.getCellByPosition( 0, 3 ).setString( "Mar" ) 
    oSheet.getCellByPosition( 0, 4 ).setString( "Apr" ) 
    oSheet.getCellByPosition( 0, 5 ).setString( "May" ) 
    oSheet.getCellByPosition( 0, 6 ).setString( "Jun" ) 
    oSheet.getCellByPosition( 0, 7 ).setString( "Jul" ) 
    oSheet.getCellByPosition( 0, 8 ).setString( "Aug" ) 
    oSheet.getCellByPosition( 0, 9 ).setString( "Sep" ) 
    oSheet.getCellByPosition( 0, 10 ).setString( "Oct" ) 
    oSheet.getCellByPosition( 0, 11 ).setString( "Nov" ) 
    oSheet.getCellByPosition( 0, 12 ).setString( "Dec" ) 

    oSheet.getCellByPosition( 1, 1 ).setValue( 3826.37 ) 
    oSheet.getCellByPosition( 1, 2 ).setValue( 3504.21 ) 
    oSheet.getCellByPosition( 1, 3 ).setValue( 2961.45 ) 
    oSheet.getCellByPosition( 1, 4 ).setValue( 2504.12 ) 
    oSheet.getCellByPosition( 1, 5 ).setValue( 2713.98 ) 
    oSheet.getCellByPosition( 1, 6 ).setValue( 2248.17 ) 
    oSheet.getCellByPosition( 1, 7 ).setValue( 1802.13 ) 
    oSheet.getCellByPosition( 1, 8 ).setValue( 2003.22 ) 
    oSheet.getCellByPosition( 1, 9 ).setValue( 1502.54 ) 
    oSheet.getCellByPosition( 1, 10 ).setValue( 1207.68 ) 
    oSheet.getCellByPosition( 1, 11 ).setValue( 1319.71 ) 
    oSheet.getCellByPosition( 1, 12 ).setValue( 786.03 ) 

    oSheet.getCellByPosition( 2, 1 ).setFormula( "=DATE(2004;01;31)" ) 
    oSheet.getCellByPosition( 2, 2 ).setFormula( "=DATE(2004;02;29)" ) 
    oSheet.getCellByPosition( 2, 3 ).setFormula( "=DATE(2004;03;31)" ) 
    oSheet.getCellByPosition( 2, 4 ).setFormula( "=DATE(2004;04;30)" ) 
    oSheet.getCellByPosition( 2, 5 ).setFormula( "=DATE(2004;05;31)" ) 
    oSheet.getCellByPosition( 2, 6 ).setFormula( "=DATE(2004;06;30)" ) 
    oSheet.getCellByPosition( 2, 7 ).setFormula( "=DATE(2004;07;31)" ) 
    oSheet.getCellByPosition( 2, 8 ).setFormula( "=DATE(2004;08;31)" ) 
    oSheet.getCellByPosition( 2, 9 ).setFormula( "=DATE(2004;09;30)" ) 
    # Note that these last three dates are not set as DATE() function calls. 
    oSheet.getCellByPosition( 2, 10 ).setFormula( "10/31/2004" ) 
    oSheet.getCellByPosition( 2, 11 ).setFormula( "11/30/2004" ) 
    oSheet.getCellRangeByName( "C13" ).setFormula( "12/31/2004" ) 
    #----- 

    #----- 
    # Format the date cells as dates. 
    com_sun_star_util_NumberFormat_DATE = uno.getConstantByName( "com.sun.star.util.NumberFormat.DATE" ) 
    oFormats = oDoc.getNumberFormats() 
    oLocale = createUnoStruct( "com.sun.star.lang.Locale" ) 
    nDateKey = oFormats.getStandardFormat( com_sun_star_util_NumberFormat_DATE, oLocale ) 
    oCell = oSheet.getCellRangeByName( "C2:C13" ) 
    oCell.NumberFormat = nDateKey 
    #----- 
    
    #----- 
    # Now add a chart to the spreadsheet. 

    oCellRangeAddress = oSheet.getCellRangeByName( "A1:B13" ).getRangeAddress() 
    # oCellRangeAddress = MakeCellRangeAddress( 0, 0, 1, 1, 12 ) 
    # Get the collection of charts from the sheet. 
    oCharts = oSheet.getCharts() 
    # Add a new chart with a specific name, 
    #  in a specific rectangle on the drawing page, 
    #  and connected to specific cells of the spreadsheet. 
    oCharts.addNewByName( "Sales", 
               makeRectangle( 8000, 1000, 16000, 10000 ), 
               Array( oCellRangeAddress ), 
               True, True ) 
    # From the collection of charts, get the new chart we just created. 
    oChart = oCharts.getByName( "Sales" ) 
    # Get the chart document model. 
    oChartDoc = oChart.getEmbeddedObject() 

    # Get the drawing text shape of the title of the chart. 
    oTitleTextShape = oChartDoc.getTitle() 
    # Change the title. 
    oTitleTextShape.String = "Sales Chart" 

    # Create a diagram. 
    oDiagram = oChartDoc.createInstance( "com.sun.star.chart.BarDiagram" ) 
    # Set its parameters. 
    oDiagram.Vertical = True 
    # Make the chart use this diagram. 
    oChartDoc.setDiagram( oDiagram ) 

    # Ask the chart what diagram it is using. 
    # (Unnecessary, since variable oDiagram already contains this value.) 
    oDiagram = oChartDoc.getDiagram() 
    # Make more changes to the diagram. 
    oDiagram.DataCaption = uno.getConstantByName( "com.sun.star.chart.ChartDataCaption.VALUE" ) 
    oDiagram.DataRowSource = uno.getConstantByName( "com.sun.star.chart.ChartDataRowSource.COLUMNS" ) 
    # 
    #----- 


    #----- 
    # Now demonstrate how to manipulate the sheets. 

    # Insert six more sheets into the document. 
    nNumSheetsCurrently = oDoc.getSheets().getCount() 
    oDoc.getSheets().insertNewByName( "Fred", nNumSheetsCurrently+1 ) 
    oDoc.getSheets().insertNewByName( "Joe", nNumSheetsCurrently+2 ) 
    oDoc.getSheets().insertNewByName( "Bill", nNumSheetsCurrently+3 ) 
    oDoc.getSheets().insertNewByName( "Sam", nNumSheetsCurrently+4 ) 
    oDoc.getSheets().insertNewByName( "Tom", nNumSheetsCurrently+5 ) 
    oDoc.getSheets().insertNewByName( "David", nNumSheetsCurrently+6 ) 
    # Now find a sheet named "Sheet2" and get rid of it. 
    oDoc.getSheets().removeByName( "Sheet2" ) 
    # Now find the sheet named "Sam" and change its name to "Sheet 37" 
    oDoc.getSheets().getByName( "Sam" ).Name = "Sheet 37" 
    # 
    #----- 

    #------- 
    # Now print the document -- three different ways. 

    # Technique 1. 
    # Now print the document. 
    # Print two copies. 
    # Print pages 1 thru 4, and also page 10. 
    # 
    # NOTE: we would do it like this, except the word "print" 
    #       has a special meaning in python, and cannot be invoked 
    #       as a method. 
    #oDoc.print( 
    #    Array( 
    #        makePropertyValue( "CopyCount", 2 ), 
    #        makePropertyValue( "Pages", "1-4;10" ) ) ) 
    uno.invoke( oDoc, "print", ( Array( 
            makePropertyValue( "CopyCount", 2 ), 
            makePropertyValue( "Pages", "1-4;10" ) ), ) ) 

    # Technique 2. 
    # Print the document already, without any arguments. 
    uno.invoke( oDoc, "print", ( Array(), ) ) 
    #oDoc.print( Array() ) 

    # Using technique 1 or 2, be sure not to close the document 
    #  until printing is completed. 
    #    http://www.oooforum.org/forum/viewtopic.php?p=23144#23144 


    # Technique 3. 
    # Print the document by bringing up the Print Job dialog box 
    #  for the user to interact with. 
    oDocFrame = oDoc.getCurrentController().getFrame() 
    oDispatchHelper = createUnoService( "com.sun.star.frame.DispatchHelper" ) 
    oDispatchHelper.executeDispatch( oDocFrame, ".uno:Print", "", 0, Array() ) 
    # To learn some more about the dispatcher, see these articles... 
    #    http://www.oooforum.org/forum/viewtopic.php?t=5058 
    #    http://www.oooforum.org/forum/viewtopic.php?t=5057 

    # 
    #------- 

    #------- 
    # Now save the document 

    # Prepare the filename to save. 
    # We're going to save the file in several different formats, 
    #  but all based on the same filename. 
    cFile = "C:\Documents and Settings\dbrewer\Desktop\MyCalc" # Windows 
    #cFile = "/home/danny/Desktop/MyCalc.sxc" # Linux 

    # Now save the spreadsheet in native OOo Calc format. 
    cURL = convertToURL( cFile + ".sxc" ) 
    oDoc.storeAsURL( cURL, Array() ) 

    # Note the above used storeAsUrl, 
    #  the following use storeToUrl. 

    # Now save it in Excel format. 
    cURL = convertToURL( cFile + ".xls" ) 
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "MS Excel 97" ) ) ) 

    # Now save a PDF. 
    cURL = convertToURL( cFile + ".pdf" ) 
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "calc_pdf_Export" ) ) ) 

    # Now save it in CSV format. 
    cURL = convertToURL( cFile + ".csv" ) 
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "Text - txt - csv (StarCalc)" ) ) ) 

    # Now save it in DIF format. 
    cURL = convertToURL( cFile + ".dif" ) 
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "DIF" ) ) ) 

    # Now save it in SYLK format. 
    cURL = convertToURL( cFile + ".sylk" ) 
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "SYLK" ) ) ) 

    # Now save as HTML. 
    cURL = convertToURL( cFile + ".html" ) 
    oDoc.storeToURL( cURL, Array( makePropertyValue( "FilterName", "HTML (StarCalc)" ) ) ) 

    # A list of some filter names you can use for both loading 
    #  and saving a document can be found here... 
    #    http://www.oooforum.org/forum/viewtopic.php?t=3549 

    # 
    #------- 


    #------- 
    # Now close the document 
    oDoc.close( True ) 
    #------- 





# import Danny.OOo.Examples.CalcExamples 
# reload( Danny.OOo.Examples.CalcExamples ); from Danny.OOo.Examples.CalcExamples import * 

# CalcExample() 