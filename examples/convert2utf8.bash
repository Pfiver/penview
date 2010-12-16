#!/bin/bash

file=$1
/usr/bin/iconv --from-code=ISO-8859-1 --to-code=UTF-8 ./$file > ./$file.1; mv ./$file.1 ./$file
