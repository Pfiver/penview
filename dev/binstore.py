#!/usr/bin/python

from sys import argv, stdin, stdout
from struct import calcsize, pack, unpack

def printbin(numbers, fmt="i"):

    out = ""
    for n in numbers:
	    out += pack(fmt, n)

    stdout.write(out)

def parsebin(data, fmt="i"):

    out = ""
    elmsz = calcsize(fmt)

    while len(data):
	out += " %d" % unpack(fmt, data[:elmsz])[0]
	data = data[elmsz:]

    print out

def switch(index, map):
    map[index]()

def write():
    printbin(range(0, 10, 2))

def read():
    parsebin(stdin.read())

switch(argv[1], {
	"read": read,
	"write": write,
})

# vim:sw=4

# example usage: ./binstore.py write | ./binstore.py read
