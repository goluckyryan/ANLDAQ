#!/bin/bash -l

##overall control variable to enable/disable error checking.
PERFORM_ERROR_CHECKS=0

##overall control variable to set verbosity of output to screen
##
##    Nominal rules : 2+ = everything
##                    1  = steps within stages but no per-channel messages
##                    0  = Only stage level messages or errors
SCRIPT_VERBOSITY=1

##name of log file for all caput/caget messages  (use NUL: to not save anything)
SCRIPT_LOG_FILE="scr.txt"

##enumeration variable defining which SERDES links are in use in the master trigger.
##in each line the first string is the device to which the link is connected, the 
##second string is the name of the link.  As this list is parsed the rule is that
##any string more than 1 character long is assumed to be a "name", but any string
##that is exactly 1 character long is a "link name" that's part of a PV.  
##
##    If the "link name" is "X" that is interpreted as "this link is not used" but
##    otherwise the link is assumed to be used.
##
##    It is not explicitly assumed that the first string will be used to make a PV name
##  for links L, R and U, but is just for text output. 
##
##    It IS assumed that for links A-H the "name" string is the actual name of the device
##    within the DGS system.
##  
##    Link A is unused.
##    Link B is unused.
##    Link C is unused.
##    Link D drives link L of RTR1.
##    Link E is unused. 
##    Link F is unused. 
##    Link G is unused. 
##    Link H is unused. 
##    Link L is unused. 
##    Link R is unused.
##    Link U is unused.

MT_LINK_MAP=(

"MASKED"      "A"
"MASKED"      "B"
"MASKED"      "C"
"RTR1"      "D"
"MASKED"    "E"
"MASKED"    "F"
"MASKED"    "G"
"MASKED"    "H"
"MASKED"    "L"
"MASKED"       "R"
"MASKED"      "U"
)

#enabled or disabled remote trigger propagation for each remote system
PROPAGATE_TRIG_FROM_DUB=0
PROPAGATE_TRIG_FROM_DFMA=0
PROPAGATE_TRIG_FROM_DXA=0

#0:use local clock  1:use remote (link) clock
MT_USE_LINK_CLK=0

## variable to control which clock the script sets all digitizers to.
## 0: AUX
## 1: Serdes
## 2: Oscillator
## 3: Serdes
DIG_CLOCK_SEL=1

