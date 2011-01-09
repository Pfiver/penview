#!/bin/bash

topdir="$(readlink -f .)"			# (absolute) path to "Messdaten" directory

groups=("Marc Patrick" "Mario Moriz")		# names of group directories to be processed

utilsdir="$(readlink -f ../../.penview/utils)"	# (absolute) path to the penview/utils directory

# _convert()					# converter function
#
# for all groups, convert all files in a group directory under $1, matching the shell glob expression $2
# into another format and store them in a group directory under $3
# removing all existing files there and using the command $4

_convert() {
	echo destination: "$3"
	mkdir -p "$3"				# create the destionation format directory if it doesn't exist
	pushd "$3" > /dev/null			# change into the destionation format directory
	for group in "${groups[@]}"		# do the next block for each group
	do
		echo group: $group
		rm -rf "$group"			# unconditionally remove the group directory if it exists
		mkdir "$group"			# recreate the group directory
		pushd "$group" > /dev/null	# cd into the group directory
		"$4" "$topdir/$1/$group"/$2	# do the actual work
		popd > /dev/null
	done
	popd > /dev/null
}

# _overview()
#
# make some sql queries on the converted data to generate a simple overview of the content

_overview() {
	for f in SQLite/*/*.sqlite
	do {
		echo "select '${f##*SQLite/}:';"
		echo "select ' nvalues: '||count(*) from 'values';"
		echo "select case when (select t from 'values' limit 1) is null"
		echo " then ' [no time values]' else"
		echo "  (select ' time_0: '||t from 'values' limit 1) ||'"$'\n'"'||"
		echo "  (select ' time_n: '||t from 'values' where rowid = (select max(rowid) from 'values'))"
		echo "end;"
		for n in v{1,2,3,4,5,6,7,8,9}_{desc,unit}
		do echo "select ' '||name||': '||value from metadata where name like '$n' and value != '';"
		done
	    } | sqlite3 "$f"
	done
}

cd "$topdir"

shopt -s extglob				# make extended glob patterns like "!(*.metadata).csv" work

_convert XLS "*.xls"             CSV    "$utilsdir/xls2csv.py"
_convert CSV "!(*.metadata).csv" SQLite "$utilsdir/csv2sqlite.py"

_overview >| overview.txt
