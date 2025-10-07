#!/bin/bash -l

echo "TRIG SETUP STAGE 5 SCRIPT BEGINS"

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
##    STAGE 5: Flip digitizers and routers, in order, from sending
##    SYNC to sending "real" data. Check at each step that nothing
##    erroneous occurs.
##===================================================================

echo "------------------------------------------------------------------------------"
echo " STAGE 5: Flip digitizers and routers, in order, from sending"
echo " SYNC to sending 'real' data.  Check for errors."
echo "------------------------------------------------------------------------------"
echo ""

##------------------------------------------------------
##    5A: change digitizers from sending sync to sending discriminator bits.
##------------------------------------------------------
caput ScriptStage 5.1 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 5.1
if (( SCRIPT_VERBOSITY > 0 )); then
    echo "Stage 5a: flip digitizers to send discriminator data instead of SYNC"
fi

for DIG in ${LIST_OF_DIGITIZERS[@]}; do
    if [[ ${DIG:0:3} == "VME" ]];            ##crate names start with VME
        then
        CRATENAME=$DIG        ##save crate name for cycling through module names within crate        
        if (( SCRIPT_VERBOSITY > 1 )); then
            echo "Setting digitizers in crate $CRATENAME"
        fi
    else    ##is X, MDIGn or SDIGn
        if [[ ${DIG} != "X" ]];            ##skip if X
        then
            caput -t ${CRATENAME}:${DIG}:sd_sync 0 > /dev/null    ##turn OFF SYNC control bit to DS92LV18
        fi ## end of if [[ ${DIG} != "X" ]];
    fi    ##end if if [[ ${DIG:0:3} == "VME" ]];
done    ##for DIG in ${LIST_OF_DIGITIZERS[@]}; do

##------------------------------------------------------
##    5B: After switching digitizer data, re-verify that all links of router are happy.
##------------------------------------------------------

if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    caput ScriptStage 5.2 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 5.2
    ERRORFLAG=0
    sleep 2.0        ##ensure EPICS has had a chance to refresh all the PVs
    if (( SCRIPT_VERBOSITY > 0 )); then
        echo "Stage 5B: re-test router link-init machines after switching digitizer to data not SYNC"
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
        echo "Stage 5B: ${ERRORFLAG} routers did not return to ALL_LOCK"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    fi     
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];    

## Go through and hit retry, then ack, on all the router link-init machines

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
##    5C: change the routers to be sending real data, not SYNC.
##    Verify the master trigger is still happy thereafter.
##------------------------------------------------------
caput ScriptStage 5.3 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 5.3
if (( SCRIPT_VERBOSITY > 0 )); then
    echo "Stage 5C: Change routers to send real data, not SYNC, to master trigger"
fi

for RTR in ${LIST_OF_ROUTERS[@]}; do
    ##only use $RTR if it is the name of a router in the system
    if [[ ${RTR:6:3} == "RTR" ]]; 
    then
        if (( SCRIPT_VERBOSITY > 1 )); then
            echo "Removing SYNC from router $RTR, link L"
        fi
        caput -t ${RTR}:LRUCtl02 OFF >> ${SCRIPT_LOG_FILE}    ##turn off SYNC        
    fi    ##end of if [[ ${RTR:6:3} == "RTR" ]];
done

#Disable SYNCs
caput -t ${MT_VME_LEADER}:MTRG:LRUCtl02 0 >> ${SCRIPT_LOG_FILE}        #link L Sync
caput -t ${MT_VME_LEADER}:MTRG:LRUCtl06 0 >> ${SCRIPT_LOG_FILE}        #link R Sync
caput -t ${MT_VME_LEADER}:MTRG:LRUCtl10 0 >> ${SCRIPT_LOG_FILE}        #link U Sync



##------------------------------------------------------
##    5D: After switching router data, re-check that master trigger is happy
##------------------------------------------------------
if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    caput ScriptStage 5.4 >> ${SCRIPT_LOG_FILE}    ##inform user we have entered stage 5.4
    if (( SCRIPT_VERBOSITY > 0 )); then
        echo "Stage 5D: Verifying state of master trigger link-init machine after router data change"
    fi
    sleep 2.0    ##        read -p "hit key to proceed"
    EXECSTR="caget -t ${MT_VME_LEADER}:MTRG:LINK_INIT_STATE_RBV"
##    echo "executing $EXECSTR"
    TEST1=$($EXECSTR)
    if [ "$TEST1" != "ACKED" ];
    then
        echo "ERROR : Master Trigger Link Init machine error: should be state ACKED, is in state $TEST1"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    fi    ##end of if [ "$TEST1" != "ALL_LOCK" ];
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];    


exit 0


