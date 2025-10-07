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
LIST_OF_ROUTERS=("VME99:RTR1" "A" "X" "X" "X" "X" "X" "X" "X" "L" "X" "X")

##enumeration variable for digitizer arrangement within system
#crate #module names (six per crate, use 'X" for unused positions
LIST_OF_DIGITIZERS=(
"VME99"    "MDIG1" "X" "X" "X" "X"     "X"
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

