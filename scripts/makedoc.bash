#!/bin/bash -e

penview="$(cd "${0%/*}/.."; pwd)"
pvpages="$penview/../penview-pages/epydoc"

rm -rf "$pvpages"
mkdir -p "$pvpages"

export PYTHONPATH="$penview/lib"

epydoc -v -o "$pvpages" --no-private --docformat restructuredtext --name PenView --url http://p2000.github.com/penview/ "$penview"/*.py

read -p "git add commit push ? "

[[ "$REPLY" == [yY]* ]] || exit

cd "$pvpages"

git add .

git commit -am "epydoc regenerated"

git push
