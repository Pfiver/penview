#!/bin/bash -e

penview="$(cd "${0%/*}/.."; pwd)"
pvpages="$penview/../penview-pages/epydoc"

rm -rf "$pvpages"
mkdir -p "$pvpages"
epydoc -o "$pvpages" --no-private --name PenView --url http://p2000.github.com/penview/ "$penview"/*.py
