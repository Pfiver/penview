#
# $Id: aquaTheme.tcl,v 1.29 2008/05/23 20:05:22 jenglish Exp $
#
# Aqua theme (OSX native look and feel)
#

namespace eval ttk::theme::aqua {
    ttk::style theme settings aqua {

	ttk::style configure . \
	    -font System \
	    -background White \
	    -foreground Black \
	    -selectbackground SystemHighlight \
	    -selectforeground SystemHighlightText \
	    -selectborderwidth 0 \
	    -insertwidth 1 \
	    ;
	ttk::style map . \
	    -foreground [list  disabled "#7f7f7f"  background "#7f7f7f"] \
	    -selectbackground [list background "#c3c3c3"  !focus "#c3c3c3"] \
	    -selectforeground [list background "#a3a3a3"  !focus "#000000"] \
	    ;

	# Workaround for #1100117:
	# Actually, on Aqua we probably shouldn't stipple images in
	# disabled buttons even if it did work...
	#
	ttk::style configure . -stipple {}

	ttk::style configure TButton -anchor center -width -6
	ttk::style configure Toolbutton -padding 4
	# See Apple HIG figs 14-63, 14-65
	ttk::style configure TNotebook -tabposition n -padding {20 12}
	ttk::style configure TNotebook.Tab -padding {10 2 10 2}

	# Combobox:
	ttk::style configure TCombobox -postoffset {5 -2 -10 0}

	# Treeview:
	ttk::style configure Heading -font TkHeadingFont
	ttk::style configure Treeview -rowheight 18 -background White
	ttk::style map Treeview -background [list \
		{selected background} "#c3c3c3" selected SystemHighlight] ;

	# Enable animation for ttk::progressbar widget:
	ttk::style configure TProgressbar -period 100 -maxphase 255

	# For Aqua, labelframe labels should appear outside the border,
	# with a 14 pixel inset and 4 pixels spacing between border and label
	# (ref: Apple Human Interface Guidelines / Controls / Grouping Controls)
	#
    	ttk::style configure TLabelframe \
		-labeloutside true -labelmargins {14 0 14 4}

	# TODO: panedwindow sashes should be 9 pixels (HIG:Controls:Split Views)
    }
}
