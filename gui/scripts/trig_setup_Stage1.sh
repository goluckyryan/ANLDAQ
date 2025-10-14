#!/bin/bash -l
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> TRIG SETUP STAGE 1 SCRIPT BEGINS"

##===================================================================
## System definition area
##
##    Bash variables define how many boards are connected where.
##===================================================================
SYSTEM_DEFINE_FILE=${1}
cd ${2}        ##2nd arg to this is the path to scripts 
echo "Loading system parameters from ${SYSTEM_DEFINE_FILE}"
source ./${SYSTEM_DEFINE_FILE}

##===================================================================
##    STAGE 1: set up master trigger to be driving Sync pattern out all links.
##
##    The general assumption at this point is that the user has intentionally and with
##    malice aforethought mangled the setup of the board to maximum degree.
##===================================================================

echo "--------------------------------------------------------------------------"
echo "  STAGE 1: set up master trigger to be driving Sync pattern out all links."
echo "--------------------------------------------------------------------------"
echo ""
##-------------------------------------------------------------------
## Clock Source - initialize to local to insure setup can occur
##-------------------------------------------------------------------
echo "################ 1A: setting master to local clock"

caput ${MT_VME_LEADER}:MTRG:ClkSrc ${MT_USE_LINK_CLK} 
####################
## propagation control logic must be all OFF for setup as a local system, F1 ON for a subservient system.
####################
caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F1 ${MT_USE_LINK_CLK}          ##remove any left-over linkage of this master trigger to another
caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F3 0 
caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F4 0 
caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F5 0 
caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F6 0 
caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F7 0 

caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F3 0 
caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F4 0 
caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F5 0 
caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F6 0 
caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F7 0 

caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F3 0 
caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F4 0 
caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F5 0 
caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F6 0 
caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F7 0 


caput ${MT_VME_LEADER}:MTRG:reg_STARTING_TIMESTAMP_HI 0 
caput ${MT_VME_LEADER}:MTRG:reg_STARTING_TIMESTAMP_MID 0 
caput ${MT_VME_LEADER}:MTRG:reg_STARTING_TIMESTAMP_LOW 0 

##------------------------------------------------------------------
##  Clear any leftover junk states in the master trigger that may exist.
##-----------------------------------------------------------------
## assert reset and then release it after setting other control bits.
echo "################ 1B: clear any leftover states in link-init of master trigger"

caput ${MT_VME_LEADER}:MTRG:RESET_LINK_INIT 1 
caput ${MT_VME_LEADER}:MTRG:LOCK_RETRY 0 
caput ${MT_VME_LEADER}:MTRG:LOCK_ACK 0 
caput ${MT_VME_LEADER}:MTRG:LINK_L_STRINGENT 0 
caput ${MT_VME_LEADER}:MTRG:LINK_R_STRINGENT 0 
caput ${MT_VME_LEADER}:MTRG:LINK_U_STRINGENT 0 
caput ${MT_VME_LEADER}:MTRG:IMP_SYNC 0 

##-------------------------------------------------------------------
# In readiness for later, clear all trigger mask bits to turn off all triggers
##-------------------------------------------------------------------
echo "################ 1C: Resetting trigger configuration to all disabled"

caput ${MT_VME_LEADER}:MTRG:EN_MAN_AUX off                  #turn off man/aux triggers
caput ${MT_VME_LEADER}:MTRG:EN_SUM_X off                  #turn off sum X triggers
caput ${MT_VME_LEADER}:MTRG:EN_SUM_Y off                  #turn off sum Y triggers
caput ${MT_VME_LEADER}:MTRG:EN_SUM_XY off                  #turn off sum X & sum Y triggers
caput ${MT_VME_LEADER}:MTRG:EN_ALGO5 off                  #turn off CPLD triggers
caput ${MT_VME_LEADER}:MTRG:EN_LINK_L off          #turn off  GITMO/LINK L
caput ${MT_VME_LEADER}:MTRG:EN_LINK_R off    #turn off  MSTR/LINK R
caput ${MT_VME_LEADER}:MTRG:EN_MYRIAD_LINK_U off         #turn off  MYRIAD/LINK U

##################
## JTA 20240223: Also ensure that all masking for coincidence trigger (Algo 5) is OFF
##################
caput ${MT_VME_LEADER}:MTRG:reg_COINC_TRIG_MASK 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_A1 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_A2 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_A3 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_A4 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_A6 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_A7 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_B1 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_B2 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_B3 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_B4 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_B6 0         ##disable all coincidence select bits
caput ${MT_VME_LEADER}:MTRG:COINC_TRIG_MASK_B7 0         ##disable all coincidence select bits

##################
## JTA 20240223: Also ensure that algo 5 is set for the coincidence trigger and Algo 8 is Remote trigger, not MyRIAD
##################
caput ${MT_VME_LEADER}:MTRG:ALGO_5_SELECT 1         ##this sets trigger algorithm 5 to coincidence trigger

##################
## JTA 20240223: Selections of mode for algorithms 6,7,8 (potential remote triggers)
##################
caput ${MT_VME_LEADER}:MTRG:LINK_L_IS_TRIGGER_TYPE 0         ##mode select for link L triggering mux (as of 20240223, must be 1 to enable remote timestamps)
caput ${MT_VME_LEADER}:MTRG:LINK_R_IS_TRIGGER_TYPE 0         ##mode select for link R triggering mux (as of 20240223, no function)
caput ${MT_VME_LEADER}:MTRG:LINK_U_IS_TRIGGER_TYPE 1         ##mode select for link U triggering mux (as of 20240223, 0=MyRIAD, 1=Remote Trigger)


##-------------------------------------------------------------------
# In readiness for later, similarly clear all sources of trigger veto.
##-------------------------------------------------------------------
echo "################ 1D: Clearing all per-algorithm enables of trigger veto"

for MT_ALGO in "A" "B" "C" "D" "E" "F" "G" "H"; do
    caput ${MT_VME_LEADER}:MTRG:EN_NIM_VETO_${MT_ALGO} OFF         #turn off NIM veto enable
    caput ${MT_VME_LEADER}:MTRG:EN_RAM_VETO_${MT_ALGO} OFF         #turn off MON7 FIFO veto enable
    caput ${MT_VME_LEADER}:MTRG:EN_THROTTLE_VETO_${MT_ALGO} OFF    #turn off throttle enable
done

echo "################ 1E: Clearing all global enables of trigger veto"

caput ${MT_VME_LEADER}:MTRG:SOFTWARE_VETO off         #turn off software veto
caput ${MT_VME_LEADER}:MTRG:EN_RAM_VETO off         #turn off VETO_RAM veto
caput ${MT_VME_LEADER}:MTRG:ENBL_MON7_VETO off        #turn off MON7 FIFO fullness veto
caput ${MT_VME_LEADER}:MTRG:ENBL_NIM_VETO off         #turn off NIM veto
caput ${MT_VME_LEADER}:MTRG:ENBL_THROTTLE_VETO off    #turn off throttle enable

##-------------------------------------------------------------------
#  The master trigger normally doesn't use links L, R or U unless it is 
#  connecting to another master trigger (e.g. link R of DGS master connected to 
#  link L of DFMA master) or a MyRIAD is connected to link U.
#
#    If master-master or master-MyRIAD is being used, the SYNC of the relevant link
#    must be turned OFF.
##-------------------------------------------------------------------
echo "################ 1F: setting master links L,R,U DEN/REN/SYNC all on"

caput ${MT_VME_LEADER}:MTRG:LRUCtl00 1         #link L DEN
caput ${MT_VME_LEADER}:MTRG:LRUCtl01 1         #link L REN
caput ${MT_VME_LEADER}:MTRG:LRUCtl02 1         #link L Sync

caput ${MT_VME_LEADER}:MTRG:LRUCtl04 1         #link R DEN
caput ${MT_VME_LEADER}:MTRG:LRUCtl05 1         #link R REN
caput ${MT_VME_LEADER}:MTRG:LRUCtl06 1         #link R Sync

caput ${MT_VME_LEADER}:MTRG:LRUCtl08 1         #link U DEN
caput ${MT_VME_LEADER}:MTRG:LRUCtl09 1         #link U REN
caput ${MT_VME_LEADER}:MTRG:LRUCtl10 1         #link U Sync

##-------------------------------------------------------------------
##    With the new setup of 2022 using the VME Fiber Expander, it is necessary
##    to enable and use the "DC Balance" logic of the master trigger when sending
##    data to the routers, or errors will occur.  This shouldn't matter while sending
##    SYNC patterns, but is needed once the master trigger is sending the TTCL.
##-------------------------------------------------------------------
caput ${MT_VME_LEADER}:MTRG:EN_RTR_DCBAL 1 


##-------------------------------------------------------------------
# Set input link mask register to use links as specified in MT_LINK_MAP.
#  MT_LINK_MAP is just an array of strings, so to strip out all the
#  "names" we use a length test.  "link names" by definition have a length of 1.
#  Other entries will be longer than 1, and so we then test those to set a temporary
#  variable to decide what to do with the next length-of-1 string.
#
#  the way this works is that with any given entry for MT_LINK_MAP something like
#
#    "RTR4"      "D"        ##Link D drives link L of RTR4
#    "MASKED"    "E"        ##Link E
#
#    when the "RTR4" string is read it sets MASK_FLAG to 0, so then when 
#    the "D" is read next link D is set to unmasked.  Then the next pair
#    reads "MASKED", setting the flag, so then link E will be masked.
##-------------------------------------------------------------------
MASK_FLAG=1

echo "################ 1G: Setting master trigger Input Link Mask"

for MT_LINK in ${MT_LINK_MAP[@]}; do
    if [ ${#MT_LINK} != 1 ]; then    ##if string length is >1 then we set or clear MASK_FLAG.
        if [ ${MT_LINK} == "MASKED" ]; then
##            echo "Setting mask flag 1 because link name is ${MT_LINK}; length is ${#MT_LINK}"
            ILM_MASK_FLAG=1
            XLM_MASK_FLAG=1
            YLM_MASK_FLAG=1
            PROPAGATE_TRIG_ENABLE=0
            echo "link $MT_LINK is masked"
        elif [ ${MT_LINK} == "PIXIE" ]; then
##            echo "Setting mask flag 1 because link name is ${MT_LINK}; length is ${#MT_LINK}"
            ILM_MASK_FLAG=0
            XLM_MASK_FLAG=1
            YLM_MASK_FLAG=1
            PROPAGATE_TRIG_ENABLE=0
            echo "link $MT_LINK is pixie"
        elif [ ${MT_LINK} == "DFMA" ]; then
##            echo "Setting mask flag 1 because link name is ${MT_LINK}; length is ${#MT_LINK}"
            ILM_MASK_FLAG=0
            XLM_MASK_FLAG=1
            YLM_MASK_FLAG=1
            PROPAGATE_TRIG_ENABLE=${PROPAGATE_TRIG_FROM_DFMA}
            echo "link $MT_LINK is DFMA"
        elif [ ${MT_LINK} == "DUB" ]; then
##            echo "Setting mask flag 1 because link name is ${MT_LINK}; length is ${#MT_LINK}"
            ILM_MASK_FLAG=0
            XLM_MASK_FLAG=1
            YLM_MASK_FLAG=1
            PROPAGATE_TRIG_ENABLE=${PROPAGATE_TRIG_FROM_DUB}
            echo "link $MT_LINK is DUB"
        elif [ ${MT_LINK} == "DXA" ]; then
##            echo "Setting mask flag 1 because link name is ${MT_LINK}; length is ${#MT_LINK}"
            ILM_MASK_FLAG=0
            XLM_MASK_FLAG=1
            YLM_MASK_FLAG=1
            PROPAGATE_TRIG_ENABLE=${PROPAGATE_TRIG_FROM_DXA}
            echo "link $MT_LINK is DXA"
        else
##            echo "Setting mask flag 0 because link name is ${MT_LINK}; length is ${#MT_LINK}"
            ILM_MASK_FLAG=0
            XLM_MASK_FLAG=0
            YLM_MASK_FLAG=0
            PROPAGATE_TRIG_ENABLE=0
            echo "link $MT_LINK is other (e.g. RTR)"
        fi
    
    ##If, however, the string length is 1 we assume it is a "link name" so tied to a PV name
    else
        echo "setting input link mask of link $MT_LINK to ${ILM_MASK_FLAG}"
        caput ${MT_VME_LEADER}:MTRG:ILM_${MT_LINK} ${ILM_MASK_FLAG}      #masked links have mask of 1
        ##JTA add 20240223: masked links should not participate in X/Y sums
        ##20240224: links L, R, U should not be processed here.
        if [ ${MT_LINK} != "L" ] && [ ${MT_LINK} != "R" ] && [ ${MT_LINK} != "U" ]; then
            echo "setting X/Y mask of link $MT_LINK to ${XLM_MASK_FLAG} and ${YLM_MASK_FLAG}"
            caput ${MT_VME_LEADER}:MTRG:XLM_${MT_LINK} ${XLM_MASK_FLAG}      #masked links do not participate in the X sum (1=masked, or blocked)
            caput ${MT_VME_LEADER}:MTRG:YLM_${MT_LINK} ${YLM_MASK_FLAG}      #masked links do not participate in the Y sum (1=masked, or blocked)
        fi
        
        ## JTA20240301: as the links in MT_LINK_MAP are processed, if the link is L, R or U, then set the trigger propagation
        ## from that link to 0 or 1 based upon the previously set PROPAGATE_TRIG_ENABLE
        if [ ${MT_LINK} = "L" ]; then
            echo "setting trig propagation F3 on link L to ${PROPAGATE_TRIG_ENABLE}"
            caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F3 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F4 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F5 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F6 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_L_PROPAGATE_F7 ${PROPAGATE_TRIG_ENABLE} 
        elif [ ${MT_LINK} = "R" ]; then
            echo "setting trig propagation F3 on link R to ${PROPAGATE_TRIG_ENABLE}"
            caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F3 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F4 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F5 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F6 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_R_PROPAGATE_F7 ${PROPAGATE_TRIG_ENABLE} 
        elif [ ${MT_LINK} = "U" ]; then
            echo "setting trig propagation F3 on link U to ${PROPAGATE_TRIG_ENABLE}"
            caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F3 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F4 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F5 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F6 ${PROPAGATE_TRIG_ENABLE} 
			caput ${MT_VME_LEADER}:MTRG:LINK_U_PROPAGATE_F7 ${PROPAGATE_TRIG_ENABLE} 
        fi

    fi
done

##-------------------------------------------------------------------
# Turn Transmit power and Receive power on in all links irrespective of masking
# Also insure that Line Loopback and Local Loopback are all OFF
##-------------------------------------------------------------------
echo "################ 1H: Turn master Tpwr, Rpwr all on, disable line & local loopback"

for MT_LINK in ${TRIG_ALL_LINKS[@]}; do
    caput ${MT_VME_LEADER}:MTRG:TPwr_${MT_LINK} 1 
    caput ${MT_VME_LEADER}:MTRG:RPwr_${MT_LINK} 1 
done

for MT_LINK in ${TRIG_ALL_LINKS[@]}; do
    caput ${MT_VME_LEADER}:MTRG:SLoL_${MT_LINK} 0 
    caput ${MT_VME_LEADER}:MTRG:SLiL_${MT_LINK} 0 
done


### the above sets bit-wise PVs but does not ensure the whole-register PVs match (JTA, 20230913)
caput ${MT_VME_LEADER}:MTRG:reg_SERDES_LOCAL_LE 0 
caput ${MT_VME_LEADER}:MTRG:reg_SERDES_LINE_LE 0 


##-------------------------------------------------------------------
# turn on external LVDS Pre-emphasizing drivers
#
#    Since as of July 2022 we are using the fiber expander no cable pre-emphasis is desired.
#    Use of cable pre-emphasis should not be used with fiber links, errors could result.
#
##-------------------------------------------------------------------
echo "################ 1I: Turn on Master Trigger line drivers and set pre-emphasis"

for i in 0 1 2; do
   caput ${MT_VME_LEADER}:MTRG:PrE_${i} 1 
done

caput ${MT_VME_LEADER}:MTRG:PEHLRU 0 
caput ${MT_VME_LEADER}:MTRG:PEEFG 0 
caput ${MT_VME_LEADER}:MTRG:PEABCD 0 


##remove the reset to the link-init machine
caput ${MT_VME_LEADER}:MTRG:RESET_LINK_INIT 0 

##-------------------------------------------------------------------
### at this point Master is driving SYNC patterns to all Routers
### and is waiting for Routers to send signals back.
##-------------------------------------------------------------------

exit 0

