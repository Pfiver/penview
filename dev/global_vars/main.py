app_name = "PenView"
debug_flag = True

import logging
def debug(*args):
	logging.debug(*args)

if __name__ == "__main__":
	import sys
	if len(sys.argv) > 1 and \
	   sys.argv[1].startswith("-w"):
		import main
		main.debug_flag = False
	else:
		print "it will work only if you pass a '-work' argument !"
		from main import debug_flag
		debug_flag = False

	print "main: debug_flag: " + str(debug_flag)

	# loggin works in any case
	logging.basicConfig(format=None, level=0)

	from module import cls
	cls()

