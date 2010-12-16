#!/bin/bash

cwd=`pwd`
soffice -accept=socket,host=localhost,port=8100\;urp &
#sleep 5
#/usr/bin/python $cwd/xls2csv.py $1

exit 0
