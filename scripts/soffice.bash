#!/bin/bash

cwd=`pwd`
soffice -accept=socket,host=localhost,port=8100\;urp &
sleep 5
dir="/home/archon/Desktop/Marc Patrick"
cd "$dir"
/usr/bin/python $cwd/xls2csv.py *.xls

exit 0