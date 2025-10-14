#!/bin/bash -l

## enumeration variable for loops that must touch all SERDES links in a trigger.  Do not change.
TRIG_ALL_LINKS=("A" "B" "C" "D" "E" "F" "G" "H" "L" "R" "U")

TRIG_LOCAL_LINKS=("A" "B" "C" "D" "E" "F" "G" "H")

#name of VME crate master trigger is found in
MT_VME_LEADER="VME99"

## enumeration variable defining how many Routers are in the system and which links of
## each Router are in use.  
#
# X = Unused, not driven.
# M = Masked, but link is powered on.
# A-H, L, R, U = Link is connected, unmasked, active.
##                  name       A   B   C   D   E   F   G   H   L   R   U
LIST_OF_ROUTERS=("VME99:RTR1" "A" "B" "X" "X" "X" "X" "X" "X" "L" "X" "X")

##enumeration variable for digitizer arrangement within system
#crate #module names (six per crate, use 'X" for unused positions
LIST_OF_DIGITIZERS=(
"VME99"    "MDIG1" "MDIG2" "X" "X" "X"     "X"
)

LIST_OF_DETECTOR_GS_NUMBERS=(
)

#VME GS is the nominal GS number associtate with a given VME channel, prior to remaps.
VME_GS_TO_STRIPE_LOOKUP=(
)

#VME GS is the nominal GS number associtate with a given VME channel, prior to remaps.
VME_GS_TO_PORT_LOOKUP=(
)

#VME GS is the nominal GS number associtate with a given VME channel, prior to remaps.
VME_GS_TO_COLL_GS_LOOKUP=(
)

LIST_OF_COLLECTOR_GS_NUMBERS=(
)

LIST_OF_VME_NUMBERS=("99"
)


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
"RTR1"        "D"
"MASKED"      "E"
"MASKED"      "F"
"MASKED"      "G"
"MASKED"      "H"
"MASKED"      "L"
"MASKED"      "R"
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


##overall control variable to enable/disable error checking.
PERFORM_ERROR_CHECKS=0
