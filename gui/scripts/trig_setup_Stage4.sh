#!/bin/bash -l

echo "TRIG SETUP STAGE 4 SCRIPT BEGINS"

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
##    STAGE 4: Set up all links in digitizers to be sending SYNC to Router
##    and verify that Router sees lock in all enabled links.
##===================================================================

echo "------------------------------------------------------------------------------"
echo " STAGE 4: Set up all links in digitizers to be sending SYNC to Router"
echo " and verify that Router sees lock in all enabled links."
echo "------------------------------------------------------------------------------"
echo ""

##------------------------------------------------------
##    4A: set up the digitizers
##------------------------------------------------------
if (( SCRIPT_VERBOSITY > 0 )); then
    echo "Stage 4A: initialize serdes logic of all digitizers"
fi
caput ScriptStage 4.1 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 4.1
for DIG in ${LIST_OF_DIGITIZERS[@]}; do
    if [[ ${DIG:0:3} == "VME" ]];            ##crate names start with VME
        then
        CRATENAME=$DIG        ##save crate name for cycling through module names within crate        
        if (( SCRIPT_VERBOSITY > 1 )); then
            echo "Now initializing digitizers in crate $CRATENAME"
        fi
    else    ##is X, MDIGn or SDIGn
        if [[ ${DIG} != "X" ]];            ##skip if X
        then
        caput -t ${CRATENAME}:${DIG}:clk_select 1 > null                ##Set digitizer clock to EXT/REF
        caput -t ${CRATENAME}:${DIG}:sd_rx_pwr 0 >> ${SCRIPT_LOG_FILE}                ##turn on RX power
        caput -t ${CRATENAME}:${DIG}:sd_local_loopback_en 0 >> ${SCRIPT_LOG_FILE}    ##turn off local loopback
        caput -t ${CRATENAME}:${DIG}:sd_pem 0 >> scr_txt                ##set pre-emphasis minimum
        caput -t ${CRATENAME}:${DIG}:sd_tx_pwr 0 >> ${SCRIPT_LOG_FILE}                ##turn on tx power
        caput -t ${CRATENAME}:${DIG}:sd_sync 1 >> ${SCRIPT_LOG_FILE}                ##turn on SYNC control bit to DS92LV18
        caput -t ${CRATENAME}:${DIG}:sd_line_loopback_en 0 >> ${SCRIPT_LOG_FILE}    ##turn off line loopback
        caput -t ${CRATENAME}:${DIG}:sd_sm_stringent_lock 0 >> ${SCRIPT_LOG_FILE}    ##turn off state machine stringent locking
        caput -t ${CRATENAME}:${DIG}:dc_balance_enable 0 >> ${SCRIPT_LOG_FILE}        ##turn off dc balance logic
        caput -t ${CRATENAME}:${DIG}:master_logic_enable 0 > null        ##turn off master logic enable
        fi ## end of if [[ ${DIG} != "X" ]];
    fi    ##end if if [[ ${DIG:0:3} == "VME" ]];
done    ##for DIG in ${LIST_OF_DIGITIZERS[@]}; do

sleep 2.0        ##wait for EPICS


##------------------------------------------------------
##    4B: reset router link-init machines so that Router is sending Sync pattern to all digitizers
##------------------------------------------------------

if (( SCRIPT_VERBOSITY > 0 )); then
    echo "Stage 4B: reset all router link-init machines"
fi
caput ScriptStage 4.2 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 4.2
for RTR in ${LIST_OF_ROUTERS[@]}; do
    ##only use $RTR if it is the name of a router in the system
    if [[ ${RTR:6:3} == "RTR" ]]; then
        if (( SCRIPT_VERBOSITY > 1 )); then
            echo "pulsing link_init reset to router $RTR"
        fi
        caput -t ${RTR}:RESET_LINK_INIT 0 >> ${SCRIPT_LOG_FILE}
        caput -t ${RTR}:RESET_LINK_INIT 1 >> ${SCRIPT_LOG_FILE}
        caput -t ${RTR}:RESET_LINK_INIT 0 >> ${SCRIPT_LOG_FILE}
    fi    ##end of if [[ ${RTR:6:3} == "RTR" ]]; then
done  ## end for RTR in ${LIST_OF_ROUTERS[@]}; do

sleep 2.0
##------------------------------------------------------
##    4C: Verify that all router links in range A-H that are in use are locked
##------------------------------------------------------
caput ScriptStage 4.3 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 4.3

if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    ERRORFLAG=0
    if (( SCRIPT_VERBOSITY > 0 )); then
        echo "Stage 4C: test LOCK state of all links A-H in each router selected for use"
    fi
    for RTR in ${LIST_OF_ROUTERS[@]}; do
        ##only use $RTR if it is the name of a router in the system
        if [[ ${RTR:6:3} == "RTR" ]]; 
        then
            RTRNAME=$RTR        ##save current router name
        else
            if [[ ${RTR} != "X" ]]; 
            then
                if (( SCRIPT_VERBOSITY > 1 )); then
                    echo "Testing link lock state of link $RTR in router $RTRNAME"
                fi
                EXECSTR="caget -t ${RTRNAME}:LOCK_${RTR}_RBV"
##                echo "executing $EXECSTR"
                TEST1=$($EXECSTR)
                #the LOCK_*_RBV is the actual LOCK* signal from the DS92LV18 chip,
                #so Off is a value of '0' which means LOCKED.
                if [ "$TEST1" != "Off" ];
                then
                       echo "ERROR : Router $RTRNAME Link $RTR is NOT locked"
                       ((ERRORFLAG=ERRORFLAG+1))
                fi    ##end if [ "$TEST1" != "Off" ];
            fi    ##end of if [[ ${RTR} != "X" ]];
        fi    ##end of if [[ ${RTR:6:3} == "RTR" ]];
    done
    ##--------------------------------
    ## if ERRORFLAG is not zero, abort here.
    ##--------------------------------

    if [ $ERRORFLAG != 0 ]; then
        echo "Stage 4b failure : $ERRORFLAG links not locked"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        echo "Script exit"
        exit 1
    fi     
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];    


##------------------------------------------------------
##    4D: With routers all sending Sync pattern to all digitizers, now test digitizers
##    for lock indication
##------------------------------------------------------
caput ScriptStage 4.4 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 4.4

if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    ERRORFLAG=0
    if (( SCRIPT_VERBOSITY > 0 )); then
        echo "Stage 4d: test LOCK state of all links in digitizers"
    fi
    for DIG in ${LIST_OF_DIGITIZERS[@]}; do
        if [[ ${DIG:0:3} == "VME" ]];            ##crate names start with VME
            then
            CRATENAME=$DIG        ##save crate name for cycling through module names within crate        
        else    ##is X, MDIGn or SDIGn
            if [[ ${DIG:0:3} == "MDIG" ]];            ##skip if X or SDIG
                then
                if (( SCRIPT_VERBOSITY > 1 )); then
                    echo "Testing link lock state of $CRATENAME:$DIG"
                fi
                EXECSTR="caget -t ${CRATENAME}:${DIG}:serdes_lock_RBV"
##                echo "executing $EXECSTR"
                TEST1=$($EXECSTR)
                if [ "$TEST1" != "Lock" ];
                    then
                       echo "ERROR :  $CRATENAME:$DIG is NOT locked"
                       ((ERRORFLAG=ERRORFLAG+1))
                fi    ##end if [ "$TEST1" != "Off" ];
            fi ## end if [[ ${DIG} != "X" ]];    
        fi    ##end if if [[ ${DIG:0:3} == "VME" ]];
    done    ##end for DIG in ${LIST_OF_DIGITIZERS[@]}; do
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];

if [ $ERRORFLAG > 0 ]; then
    echo "Stage 4D failure : $ERRORFLAG links not locked"
    caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
    caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
    echo "Script exit"
    exit 1
fi

##------------------------------------------------------
##    4E: flip the digitizers to use the SERDES clock
##------------------------------------------------------

if (( SCRIPT_VERBOSITY > 0 )); then
    echo "Stage 4e: flip digitizers to use desired clock; selection is $DIG_CLOCK_SEL (0=Serdes, 1=internal)"
fi
caput ScriptStage 4.5 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 4.5

caput GLBL:DIG:clk_select 1
caput GLBL:DIG:clk_select 0

#caput VME12:MDIG1:clk_select 1
#caput VME12:MDIG1:clk_select 0
#caput VME12:SDIG1:clk_select 1
#caput VME12:SDIG1:clk_select 0
#caput VME12:MDIG2:clk_select 1
#caput VME12:MDIG2:clk_select 0
#caput VME12:SDIG2:clk_select 1
#caput VME12:SDIG2:clk_select 0

## The above step will cause a glitch in the digitizer-to-router connection, so also
## go through and hit retry, then ack, on all the router link-init machines

for RTR in ${LIST_OF_ROUTERS[@]}; do
    ##only use $RTR if it is the name of a router in the system
    if [[ ${RTR:6:3} == "RTR" ]]; then
        if (( SCRIPT_VERBOSITY > 1 )); then
            echo "pulsing link_init retry, then ack, to router $RTR"
        fi
        caput -t ${RTR}:LOCK_RETRY 1 > null
        caput -t ${RTR}:LOCK_RETRY 0 > null
        caput -t ${RTR}:LOCK_ACK 1 > null
        caput -t ${RTR}:LOCK_ACK 0 > null
    fi    ##end of if [[ ${RTR:6:3} == "RTR" ]]; then
done  ## end for RTR in ${LIST_OF_ROUTERS[@]}; do

##------------------------------------------------------
##    4F: After switching digitizer clock, re-verify that all links of router are happy.
##------------------------------------------------------

caput ScriptStage 4.6 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 4.6

if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    ERRORFLAG=0
    sleep 2.0        ##ensure EPICS has had a chance to refresh all the PVs
    if (( SCRIPT_VERBOSITY > 0 )); then
        echo "Stage 4F: re-test router link-init machines after switching digitizer to serdes clock"
    fi
    for RTR in ${LIST_OF_ROUTERS[@]}; do
        ##only use $RTR if it is the name of a router in the system
        if [[ ${RTR:6:3} == "RTR" ]]; 
        then
            if (( SCRIPT_VERBOSITY > 1 )); then
                echo "Testing link-init machine state of router $RTR"
            fi
        EXECSTR="caget -t ${RTR}:ALL_LOCKED_RBV"
    ##    echo "executing $EXECSTR"
        TEST1=$($EXECSTR)
        if [ "$TEST1" != 1 ];
            then
                echo "ERROR : Router Trigger $RTR Link Init machine error: ALL_LOCKED is $TEST1"
                ((ERRORFLAG=ERRORFLAG+1))
            fi    ##end of if [ "$TEST1" != "ALL_LOCK" ];        else
        fi    ##end of if [[ ${RTR:6:3} == "RTR" ]];
    done
    ##--------------------------------
    ## if ERRORFLAG is not zero, abort here.
    ##--------------------------------

    if [ $ERRORFLAG != 0 ]; then
        echo "Stage 4F: ${ERRORFLAG} routers did not return to ALL_LOCK"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        echo "Script exit"
        exit 1
    fi     
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];    


##------------------------------------------------------
##    4G: With all setup complete, whack the Imperative Sync one more time, and
##      also clear the "lost lock" flags in all digitizers.
##------------------------------------------------------
caput ScriptStage 4.7 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 4.7


caput -t ${MT_VME_LEADER}:MTRG:IMP_SYNC 1 >> ${SCRIPT_LOG_FILE} 
caput -t ${MT_VME_LEADER}:MTRG:IMP_SYNC 0 >> ${SCRIPT_LOG_FILE} 

caput -t GLBL:DIG:sd_sm_lost_lock_flag_rst 1 >> ${SCRIPT_LOG_FILE} 
caput -t GLBL:DIG:sd_sm_lost_lock_flag_rst 0 >> ${SCRIPT_LOG_FILE} 

#caput VME12:MDIG1:sd_sm_lost_lock_flag_rst 1
#caput VME12:MDIG1:sd_sm_lost_lock_flag_rst 0
#caput VME12:SDIG1:sd_sm_lost_lock_flag_rst 1
#caput VME12:SDIG1:sd_sm_lost_lock_flag_rst 0
#caput VME12:MDIG2:sd_sm_lost_lock_flag_rst 1
#caput VME12:MDIG2:sd_sm_lost_lock_flag_rst 0
#caput VME12:SDIG2:sd_sm_lost_lock_flag_rst 1
#caput VME12:SDIG2:sd_sm_lost_lock_flag_rst 0

exit 0
