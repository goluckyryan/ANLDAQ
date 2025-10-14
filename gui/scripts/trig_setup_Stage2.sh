#!/bin/bash -l
echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> TRIG SETUP STAGE 2 SCRIPT BEGINS"

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
##  STAGE 2: Initialize Routers to receive data from master and send SYNC back to master.
##    During stage 2 all Routers use their local clock and do not attempt to use the clock
##  from the master trigger.
##===================================================================

echo "--------------------------------------------------------------------------------------"
echo " STAGE 2: Initialize Routers to receive data from master and send SYNC back to master."
echo "--------------------------------------------------------------------------------------"
echo ""

##------------------------------------------------------
## Stage 2A: Set each router to local clock, link L enabled and driving SYNC.
## 20230414: turn on link L reception dc balance.
##------------------------------------------------------
RTRCOUNT=0
CLK_SRC=local
echo "################ 2A: Set routers to ${CLK_SRC} clock, router link L to SYNC pattern, set mask of all Routers"

for RTR in ${LIST_OF_ROUTERS[@]}; do
    #-------------------------------------------------------------------
    #  Router board-level setups inside this if clause, because string is of form "RTRx"
    #  Bash substring extraction is done by ${<var>:<strt>:<numchar>
    #  In the LIST_OF_ROUTERS strings, the first one in each row is of the form VMExx:RTRx
    #  so we want :6:3  (e.g. "VME03:RTR1")
    #-------------------------------------------------------------------
    if [[ ${RTR:6:3} == "RTR" ]];
        then
        echo "found Router $RTR"
        ((RTRCOUNT=RTRCOUNT+1))        ##2.11, 2.12, 2.13, etc per router
        LINKCOUNT=0
        echo "Setting up router ${RTR}"
##        echo "RTRCOUNT = ${RTRCOUNT}; LINKCOUNT = ${LINKCOUNT};  SCRIPTSTAGE = ${SCRIPTSTAGE}"
        
        RTRNAME=$RTR    ##save router name for when we're cycling through the links
        RTR_LINKIDX=0
        ##-------------------------------------------------------------------
        ##    Start with router using local clock until such time as we feel safe 
        ##    to switch to using the clock from the master trigger.
        ##-------------------------------------------------------------------
        echo "setting up ${RTR} to use local clock"
        caput ${RTR}:ClkSrc ${CLK_SRC} 
        caput ${RTR}:reg_FORCE_SYNC_REG 0 
        ##-------------------------------------------------------------------
        ## Set link L of Router to drive SYNC back to Master
        ##-------------------------------------------------------------------
        echo "setting up ${RTR} to drive SYNC back to Master Trigger"
        
        ##EPICS often forgets the state of things, or becomes disconnected from the
        ##true state of the hardware, so during intialization you must set things twice -
        ##once to what you don't want, then again to what you do want.
        caput ${RTR}:LRUCtl00 OFF     ##turn off DEN
        caput ${RTR}:LRUCtl01 OFF     ##turn offREN
        caput ${RTR}:LRUCtl02 OFF     ##turn off SYNC
        caput ${RTR}:LRUCtl00 ON     ##turn on DEN
        caput ${RTR}:LRUCtl01 ON     ##turn on REN
        caput ${RTR}:LRUCtl02 ON     ##turn on SYNC


        ##-------------------------------------------------------------------
        ## turn on LVDS drivers in Router and set pre-emphasis
        ##-------------------------------------------------------------------
        echo "setting up ${RTR} link pre-emphasis"
        for i in 0 1 2; do
           caput ${RTR}:PrE_${i} 0  
           caput ${RTR}:PrE_${i} 1  
        done
        
        caput ${RTR}:PEHLRU 0  
        caput ${RTR}:PEEFG 0 
        caput ${RTR}:PEABCD 0 
        ##-------------------------------------------------------------------
        ##addition 20220711 JTA turn ON the DC balance logic (makes fiber happy)
        ##
        ##    examination of spreadsheet shows register definition in SS does not match firmware.
        ##    there should be a separate PV here.
        #
        #        As of 20220717 the spreadsheet has a PV named "LinkL_DCbal" but we haven't updated
        #        template files pending recompilation of the underlying driver.
        ##-------------------------------------------------------------------
        caput ${RTR}:LinkL_DCbal 1         #sets bit 13, the DC balance enable.  Affects ONLY link L back to Master.
                                                # A different bit in the register controls DC Balance to links A-H, R and U.

        ### the above sets bit-wise PVs but does not ensure the whole-register PVs match (JTA, 20230913)
        caput ${RTR}:reg_SERDES_LOCAL_LE 0 
        caput ${RTR}:reg_SERDES_LINE_LE 0 
           
##still within the 2.1 loop here..
           
    #-------------------------------------------------------------------
    #  Router channel-level setups inside this if clause, so ${RTR} will be the link letter
    #-------------------------------------------------------------------
    else
        ((LINKCOUNT=LINKCOUNT+1))
        if (( LINKCOUNT > 9 )); then
            LINKCOUNT=9
        fi
        
        RTR_LINK=${TRIG_ALL_LINKS[${RTR_LINKIDX}]}
        if [[ $RTR != $RTR_LINK ]] && [[ $RTR != "X" ]] && [[ $RTR != "M" ]]; then
            echo "ERROR: Link mismatch in LIST_OF_ROUTERS[]. Read:$RTR, Expected $RTR_LINK or X or M"
            if [[ $RTR == "A" ]] || [[ $RTR == "B" ]] || [[ $RTR == "C" ]] || [[ $RTR == "D" ]] || [[ $RTR == "E" ]] || [[ $RTR == "F" ]] || [[ $RTR == "G" ]] || [[ $RTR == "H" ]] || [[ $RTR == "L" ]] || [[ $RTR == "R" ]] || [[ $RTR == "U" ]]; then
                echo "Using $RTR instead of $RTR_LINK"
                RTR_LINK=$RTR
            else
                echo "ERROR: Unknown option: $RTR, using X for link $RTR_LINK"
                RTR="X"
            fi
        fi      
            	
        
        ##-------------------------------------------------------------------
        ## if $RTR is "X", this is an unused channel
        ##-------------------------------------------------------------------
        if [ $RTR == "X" ];    
        then                
            echo "disabling link index ${RTR_LINKIDX}, otherwise known as link ${RTR_LINK}"

            ##first to what you DON'T want
            caput ${RTRNAME}:ILM_${RTR_LINK} 0     #used links have mask of 0, unused mask is 1
            caput ${RTRNAME}:TPwr_${RTR_LINK} 1     ##turn off Transmit power
            caput ${RTRNAME}:RPwr_${RTR_LINK} 1  ##turn off Receive power
            caput ${RTRNAME}:SLoL_${RTR_LINK} 1  ##turn local loopback OFF
            caput ${RTRNAME}:SLiL_${RTR_LINK} 1  ##turn line loopback OFF
            ##then to what you DO want


            caput ${RTRNAME}:ILM_${RTR_LINK} 1     #used links have mask of 0, unused mask is 1
            caput ${RTRNAME}:TPwr_${RTR_LINK} 0     ##turn off Transmit power
            caput ${RTRNAME}:RPwr_${RTR_LINK} 0  ##turn off Receive power
            caput ${RTRNAME}:SLoL_${RTR_LINK} 0  ##turn local loopback OFF
            caput ${RTRNAME}:SLiL_${RTR_LINK} 0  ##turn line loopback OFF
            ((RTR_LINKIDX=RTR_LINKIDX+1))
        ##-------------------------------------------------------------------
        ## if $RTR is "M", this is an masked channel, but still powered on
        ##-------------------------------------------------------------------
        elif [ $RTR == "M" ];    
        then                
            echo "masking link index ${RTR_LINKIDX}, otherwise known as link ${RTR_LINK}"

            ##first to what you DON'T want
            caput ${RTRNAME}:ILM_${RTR_LINK} 0     #active links have mask of 1
            caput ${RTRNAME}:TPwr_${RTR_LINK} 0     ##turn off Transmit power
            caput ${RTRNAME}:RPwr_${RTR_LINK} 0  ##turn off Receive power
            caput ${RTRNAME}:SLoL_${RTR_LINK} 1  ##turn local loopback ON
            caput ${RTRNAME}:SLiL_${RTR_LINK} 1  ##turn line loopback ON
            ##then to what you DO want


            caput ${RTRNAME}:ILM_${RTR_LINK} 1     #used links have mask of 0, unused mask is 1
            caput ${RTRNAME}:TPwr_${RTR_LINK} 1     ##turn on Transmit power
            caput ${RTRNAME}:RPwr_${RTR_LINK} 1  ##turn on Receive power
            caput ${RTRNAME}:SLoL_${RTR_LINK} 0  ##turn local loopback OFF
            caput ${RTRNAME}:SLiL_${RTR_LINK} 0  ##turn line loopback OFF
            ((RTR_LINKIDX=RTR_LINKIDX+1))
        ##-------------------------------------------------------------------
        ## if $RTR is not "X", this is an active channel, so $RTR is a letter (A, B, C, etc.) and can be used directly
        ##-------------------------------------------------------------------
        else
            echo "activating link index ${RTR_LINKIDX}, otherwise known as link ${RTR_LINK}"

            ##first to what you DON'T want
            caput ${RTRNAME}:ILM_${RTR_LINK} 1     #used links have mask of 0, unused mask is 1
            caput ${RTRNAME}:TPwr_${RTR_LINK} 0     ##turn on Transmit power
            caput ${RTRNAME}:RPwr_${RTR_LINK} 0  ##turn on Receive power
            caput ${RTRNAME}:SLoL_${RTR_LINK} 1  ##turn local loopback OFF
            caput ${RTRNAME}:SLiL_${RTR_LINK} 1  ##turn line loopback OFF
            ##then to what you DO want
            caput ${RTRNAME}:ILM_${RTR_LINK} 0     #active links have mask of 1
            caput ${RTRNAME}:TPwr_${RTR_LINK} 1     ##turn on Transmit power
            caput ${RTRNAME}:RPwr_${RTR_LINK} 1  ##turn on Receive power
            caput ${RTRNAME}:SLoL_${RTR_LINK} 0  ##turn local loopback OFF
            caput ${RTRNAME}:SLiL_${RTR_LINK} 0  ##turn line loopback OFF
            ((RTR_LINKIDX=RTR_LINKIDX+1))
        fi
    fi
done

sleep 2.0
##------------------------------------------------------
## Stage 2B: clear errors in master that occur due to router changes
##------------------------------------------------------
echo "################ 2B: clear errors in master trigger that occur due to router changes"


##-----------------------------------
##  The initial setup of the router links probably has cycled the master's link-init
##  machine, so reset it again here.
##-----------------------------------
##apply the reset to the link-init machine
caput ${MT_VME_LEADER}:MTRG:RESET_LINK_INIT 1 
##remove the reset to the link-init machine
caput ${MT_VME_LEADER}:MTRG:RESET_LINK_INIT 0 




exit 0
