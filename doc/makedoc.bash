#!/bin/bash -e

cd "${0%/*}/"

penview=$PWD/..

ghpages=$PWD/gh-pages

rm -rf "$ghpages/epydoc"

mkdir -p "$ghpages/epydoc"

export PYTHONPATH="$penview/lib"

epydoc -v -o "$ghpages" --no-private --docformat restructuredtext --name PenView --url http://p2000.github.com/penview/ "$penview"/*.py

read -p "git add commit push ? "

[[ "$REPLY" == [yY]* ]] || exit

cd "$pvpages"

git add .

git commit --amend -C HEAD

git push
