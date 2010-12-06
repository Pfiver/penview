#!/usr/bin/python
# encoding: utf-8
# vim:ts=4

import sys
import sqlite3

conn = sqlite3.connect(sys.argv[1])

c = conn.cursor()

# Create table
def create():
	c.execute("""CREATE TABLE sqlite (id UNIQE INT, value TEXT)""")

# Insert a row of data
def insert():
	c.execute("""INSERT INTO sqlite VALUES (?, ?)""", (0, u"strüng"))

def read():
	c.execute("""SELECT * FROM sqlite""")
	for row in c:
		print row
		print [type(v) for v in row] 

create()
insert()
read()

# Save (commit) the changes
conn.commit()

# We can also close the cursor if we are done with it
c.close()

