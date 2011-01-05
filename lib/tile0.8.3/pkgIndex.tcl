if {[catch {package require Tcl 8.4}]} return
package ifneeded tile 0.8.3  [list load [file join $dir libtile0.8.3.dylib] tile]
