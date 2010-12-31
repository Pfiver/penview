# encoding: utf-8

import os, sys

# the script are in penview/scripts
# penview and penview/lib contain useful stuff we might like to import
#
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(os.path.join(os.path.dirname(__file__), ".."), "lib"))

try:
    debug_flag
except:
    debug_flag = False

if not debug_flag:
    def debug(*args):
        pass
else:
    def debug(*args):
        if len(args) and type(args[0]) != str:
            args = " - ".join(str(arg) for arg in args)
        frame = sys._getframe(1); func = frame.f_code.co_name
        if 'self' in frame.f_locals: func = frame.f_locals['self'].__class__.__name__ + "." + func
        print "(%s:%d) in %s(): %s" % (os.path.basename(frame.f_code.co_filename), frame.f_lineno, func, args[0] % args[1:])

def fileargs(ext):

    args = []

    if len(sys.argv) > 1:
	args = sys.argv[1:]

    if "autoargs" in locals():
        args += autoargs

    debug("args: %s" % args)

    files = []
    for arg in args:
	if os.path.isdir(arg):
	    # traverse dirarg
	    for file in os.listdir(arg):
		files += os.path.dirname(arg) + os.sep + file
	elif os.path.isfile(arg):
	    files += [arg]
	else:
	    print "ignoring '%s' - it is not a directory nor a file" % arg

    fileargs = []
    for file in files:
	if file.endswith("." + ext):
	    fileargs.append(file)
	else:
	    print "ignoring '%s' - it is not a '.%s' file" % (file, ext)

    debug("fileargs: %s" % fileargs)

    return fileargs
