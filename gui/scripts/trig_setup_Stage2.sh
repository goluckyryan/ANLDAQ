#!/bin/bash -l
echo "TRIG SETUP STAGE 2 SCRIPT BEGINS"

cd ${2}        ##2nd arg to this is the path to scripts ($EDMSCRIPTS)

echo "Loading system parameters from VME99_SYSTEM_DEFINES.sh"
source ./VME99_SYSTEM_DEFINES.sh

if [ -z "$1" ];        ##test for no argument specified.
    then
    if (( SCRIPT_VERBOSITY > 1 )); then
        echo "no configuration file specified, defaulting to DGS_CONFIG.sh"
    fi
    SYSTEM_CONFIG_FILE="./DGS_CONFIG.sh"
else
    if (( SCRIPT_VERBOSITY > 1 )); then
        echo "Using specified configuration file $1"
    fi
    SYSTEM_CONFIG_FILE=$1
fi

source ./${SYSTEM_CONFIG_FILE}
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
if (( SCRIPT_VERBOSITY > 0 )); then
    echo "2A: Set routers to ${CLK_SRC} clock, router link L to SYNC pattern, set mask of all Routers"
fi


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
        SCRIPTSTAGE="2.${RTRCOUNT}${LINKCOUNT}"
        echo "Setting up router ${RTR}"
##        echo "RTRCOUNT = ${RTRCOUNT}; LINKCOUNT = ${LINKCOUNT};  SCRIPTSTAGE = ${SCRIPTSTAGE}"
        caput ScriptStage ${SCRIPTSTAGE} >> ${SCRIPT_LOG_FILE}        ##set stage display
        
        RTRNAME=$RTR    ##save router name for when we're cycling through the links
        RTR_LINKIDX=0
        ##-------------------------------------------------------------------
        ##    Start with router using local clock until such time as we feel safe 
        ##    to switch to using the clock from the master trigger.
        ##-------------------------------------------------------------------
        if (( SCRIPT_VERBOSITY > 1 )); then
            echo "setting up ${RTR} to use local clock"
        fi
        caput -t ${RTR}:ClkSrc ${CLK_SRC} >> ${SCRIPT_LOG_FILE}
        caput -t ${RTR}:reg_FORCE_SYNC_REG 0 >> ${SCRIPT_LOG_FILE}
        ##-------------------------------------------------------------------
        ## Set link L of Router to drive SYNC back to Master
        ##-------------------------------------------------------------------
        if (( SCRIPT_VERBOSITY > 1 )); then
            echo "setting up ${RTR} to drive SYNC back to Master Trigger"
        fi
        
        ##EPICS often forgets the state of things, or becomes disconnected from the
        ##true state of the hardware, so during intialization you must set things twice -
        ##once to what you don't want, then again to what you do want.
        caput -t ${RTR}:LRUCtl00 OFF >> ${SCRIPT_LOG_FILE}    ##turn off DEN
        caput -t ${RTR}:LRUCtl01 OFF >> ${SCRIPT_LOG_FILE}    ##turn offREN
        caput -t ${RTR}:LRUCtl02 OFF >> ${SCRIPT_LOG_FILE}    ##turn off SYNC
        caput -t ${RTR}:LRUCtl00 ON >> ${SCRIPT_LOG_FILE}    ##turn on DEN
        caput -t ${RTR}:LRUCtl01 ON >> ${SCRIPT_LOG_FILE}    ##turn on REN
        caput -t ${RTR}:LRUCtl02 ON >> ${SCRIPT_LOG_FILE}    ##turn on SYNC


        ##-------------------------------------------------------------------
        ## turn on LVDS drivers in Router and set pre-emphasis
        ##-------------------------------------------------------------------
        if (( SCRIPT_VERBOSITY > 1 )); then
            echo "setting up ${RTR} link pre-emphasis"
        fi
        for i in 0 1 2; do
           caput -t ${RTR}:PrE_${i} 0 >> ${SCRIPT_LOG_FILE} 
           caput -t ${RTR}:PrE_${i} 1 >> ${SCRIPT_LOG_FILE} 
        done
        
        caput -t ${RTR}:PEHLRU 0  >> ${SCRIPT_LOG_FILE}
        caput -t ${RTR}:PEEFG 0 >> ${SCRIPT_LOG_FILE}
        caput -t ${RTR}:PEABCD 0 >> ${SCRIPT_LOG_FILE}
        ##-------------------------------------------------------------------
        ##addition 20220711 JTA turn ON the DC balance logic (makes fiber happy)
        ##
        ##    examination of spreadsheet shows register definition in SS does not match firmware.
        ##    there should be a separate PV here.
        #
        #        As of 20220717 the spreadsheet has a PV named "LinkL_DCbal" but we haven't updated
        #        template files pending recompilation of the underlying driver.
        ##-------------------------------------------------------------------
        caput -t ${RTR}:LinkL_DCbal 1 >> ${SCRIPT_LOG_FILE}        #sets bit 13, the DC balance enable.  Affects ONLY link L back to Master.
                                                # A different bit in the register controls DC Balance to links A-H, R and U.

        ### the above sets bit-wise PVs but does not ensure the whole-register PVs match (JTA, 20230913)
        caput -t ${RTR}:reg_SERDES_LOCAL_LE 0 >> ${SCRIPT_LOG_FILE}
           caput -t ${RTR}:reg_SERDES_LINE_LE 0 >> ${SCRIPT_LOG_FILE}
           
##still within the 2.1 loop here..
           
    #-------------------------------------------------------------------
    #  Router channel-level setups inside this if clause, so ${RTR} will be the link letter
    #-------------------------------------------------------------------
    else
        ((LINKCOUNT=LINKCOUNT+1))
        if (( LINKCOUNT > 9 )); then
            LINKCOUNT=9
        fi
        SCRIPTSTAGE="2.${RTRCOUNT}${LINKCOUNT}"
##        echo "RTRCOUNT = ${RTRCOUNT}; LINKCOUNT = ${LINKCOUNT};  SCRIPTSTAGE = ${SCRIPTSTAGE}"
        caput ScriptStage ${SCRIPTSTAGE} >> ${SCRIPT_LOG_FILE}        ##set stage display
        
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
            if (( SCRIPT_VERBOSITY > 1 )); then
                echo "disabling link index ${RTR_LINKIDX}, otherwise known as link ${RTR_LINK}"
            fi
            ##first to what you DON'T want
            caput -t ${RTRNAME}:ILM_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE}    #used links have mask of 0, unused mask is 1
            caput -t ${RTRNAME}:TPwr_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE}    ##turn off Transmit power
            caput -t ${RTRNAME}:RPwr_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE} ##turn off Receive power
            caput -t ${RTRNAME}:SLoL_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE} ##turn local loopback OFF
            caput -t ${RTRNAME}:SLiL_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE} ##turn line loopback OFF
            ##then to what you DO want


            caput -t ${RTRNAME}:ILM_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE}    #used links have mask of 0, unused mask is 1
            caput -t ${RTRNAME}:TPwr_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE}    ##turn off Transmit power
            caput -t ${RTRNAME}:RPwr_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE} ##turn off Receive power
            caput -t ${RTRNAME}:SLoL_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE} ##turn local loopback OFF
            caput -t ${RTRNAME}:SLiL_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE} ##turn line loopback OFF
            ((RTR_LINKIDX=RTR_LINKIDX+1))
        ##-------------------------------------------------------------------
        ## if $RTR is "M", this is an masked channel, but still powered on
        ##-------------------------------------------------------------------
        elif [ $RTR == "M" ];    
        then                
            if (( SCRIPT_VERBOSITY > 1 )); then
                echo "masking link index ${RTR_LINKIDX}, otherwise known as link ${RTR_LINK}"
            fi
            ##first to what you DON'T want
            caput -t ${RTRNAME}:ILM_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE}    #active links have mask of 1
            caput -t ${RTRNAME}:TPwr_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE}    ##turn off Transmit power
            caput -t ${RTRNAME}:RPwr_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE} ##turn off Receive power
            caput -t ${RTRNAME}:SLoL_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE} ##turn local loopback ON
            caput -t ${RTRNAME}:SLiL_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE} ##turn line loopback ON
            ##then to what you DO want


            caput -t ${RTRNAME}:ILM_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE}    #used links have mask of 0, unused mask is 1
            caput -t ${RTRNAME}:TPwr_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE}    ##turn on Transmit power
            caput -t ${RTRNAME}:RPwr_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE} ##turn on Receive power
            caput -t ${RTRNAME}:SLoL_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE} ##turn local loopback OFF
            caput -t ${RTRNAME}:SLiL_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE} ##turn line loopback OFF
            ((RTR_LINKIDX=RTR_LINKIDX+1))
        ##-------------------------------------------------------------------
        ## if $RTR is not "X", this is an active channel, so $RTR is a letter (A, B, C, etc.) and can be used directly
        ##-------------------------------------------------------------------
        else
            if (( SCRIPT_VERBOSITY > 1 )); then
                echo "activating link index ${RTR_LINKIDX}, otherwise known as link ${RTR_LINK}"
            fi
            ##first to what you DON'T want
            caput -t ${RTRNAME}:ILM_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE}    #used links have mask of 0, unused mask is 1
            caput -t ${RTRNAME}:TPwr_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE}    ##turn on Transmit power
            caput -t ${RTRNAME}:RPwr_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE} ##turn on Receive power
            caput -t ${RTRNAME}:SLoL_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE} ##turn local loopback OFF
            caput -t ${RTRNAME}:SLiL_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE} ##turn line loopback OFF
            ##then to what you DO want
            caput -t ${RTRNAME}:ILM_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE}    #active links have mask of 1
            caput -t ${RTRNAME}:TPwr_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE}    ##turn on Transmit power
            caput -t ${RTRNAME}:RPwr_${RTR_LINK} 1 >> ${SCRIPT_LOG_FILE} ##turn on Receive power
            caput -t ${RTRNAME}:SLoL_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE} ##turn local loopback OFF
            caput -t ${RTRNAME}:SLiL_${RTR_LINK} 0 >> ${SCRIPT_LOG_FILE} ##turn line loopback OFF
            ((RTR_LINKIDX=RTR_LINKIDX+1))
        fi
    fi
done

sleep 2.0
##------------------------------------------------------
## Stage 2B: clear errors in master that occur due to router changes
##------------------------------------------------------
caput ScriptStage 2.3 >> ${SCRIPT_LOG_FILE}        ##set stage display

if (( SCRIPT_VERBOSITY > 0 )); then
    echo "2B: clear errors in master trigger that occur due to router changes"
fi


##-----------------------------------
##  The initial setup of the router links probably has cycled the master's link-init
##  machine, so reset it again here.
##-----------------------------------
##apply the reset to the link-init machine
caput -t ${MT_VME_LEADER}:MTRG:RESET_LINK_INIT 1 >> ${SCRIPT_LOG_FILE}
##remove the reset to the link-init machine
caput -t ${MT_VME_LEADER}:MTRG:RESET_LINK_INIT 0 >> ${SCRIPT_LOG_FILE}



sleep 3.0         ##wait for EPICS to update after all those caputs...


exit 0
