#!/bin/bash -e

penview=$(cd "${0%/*}/.."; pwd)

cd "$penview/penview-pages/epydoc"

epydoc --no-private $penview
