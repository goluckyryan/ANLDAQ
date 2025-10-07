#!/bin/bash -l
echo "TRIG SETUP STAGE 3 SCRIPT BEGINS"

cd ${2}        ##2nd arg to this is the path to scripts ($EDMSCRIPTS)

echo "Loading system parameters from VME99_SYSTEM_DEFINES.sh"
source ./DGS_SYSTEM_DEFINES.sh

if [ -z "$1" ];        ##test for no argument specified.z
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
##    STAGE 3: with all trigger boards turned on, all links set up and all drivers enabled,
##    read and check the lock status of all active links.  
##
##    exit if any link that should be locked is not.
##===================================================================

echo "------------------------------------------------------------------------------"
echo " STAGE 3: with all boards turned on, all links set up and all drivers enabled,"
echo " read and check the lock status of all active links. "
echo "------------------------------------------------------------------------------"
echo ""

##------------------------------------------------------
## stage 3A: check that all the links of the master that should be locked, are.
## This is not a stringent check because EPICS only scans the lock state every second
## or so.  We will check the firmware's more stringent checking if this passes.
##------------------------------------------------------
if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    caput ScriptStage 3.1 >> ${SCRIPT_LOG_FILE}
    if (( SCRIPT_VERBOSITY > 0 )); then
        echo "3A: Check lock state of master trigger links"
    fi
    ERRORFLAG=0

    sleep 1.0    ##    read -p "hit key to proceed"
    for MT_LINK in ${MT_LINK_MAP[@]}; do
        if [ ${#MT_LINK} != 1 ]; then    ##if string length is >1 then we set or clear MASK_FLAG.
            if [ ${MT_LINK} == "MASKED" ]; then
                MASK_FLAG=1
            else
                MASK_FLAG=0
            fi    ##end of     if [ ${MT_LINK} == "MASKED" ]; 
            
        ##else case executes if length of string is 1, and thus must be a link name
        else
            if [ $MASK_FLAG == 0 ]; 
                then
                if (( SCRIPT_VERBOSITY > 1 )); then
                    echo "Testing link lock state of unmasked link ${MT_LINK}"
                fi
                    EXECSTR="caget -t ${MT_VME_LEADER}:MTRG:LOCK_${MT_LINK}_RBV"
##                    echo "executing $EXECSTR"
                    TEST1=$($EXECSTR)
##                    echo "Link ${MT_LINK} state is ${TEST1}"
                    #the LOCK_*_RBV is the actual LOCK* signal from the DS92LV18 chip,
                    #so Off is a value of '0' which means LOCKED.
                    if [ "$TEST1" != "Off" ];
                    then
                        if (( SCRIPT_VERBOSITY > 0 )); 
                        then
                            echo "ERROR : Master Trigger Link $MT_LINK is NOT locked"
                        fi
                       ((ERRORFLAG=ERRORFLAG+1))
                    fi    ##end if [ "$TEST1" != "Off" ];
            fi    ##end of if [ $MASK_FLAG == 0 ]
        fi    ##end of if [ ${#MT_LINK} != 1 ];
    done    
    
    ##--------------------------------
    ## if ERRORFLAG is not zero, abort here.
    ##--------------------------------

    if [ $ERRORFLAG != 0 ]; then
        echo "Stage 3a failure : $ERRORFLAG links not locked"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    fi     
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];    


##------------------------------------------------------
## stage 3B: check that link L of every router is locked.  Again this is not a stringent check
## because the update rate of EPICS is too slow.
##------------------------------------------------------
if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    caput ScriptStage 3.2 >> ${SCRIPT_LOG_FILE}
    if (( SCRIPT_VERBOSITY > 0 )); then
        echo "Stage 3b: test LOCK state of link L in all routers"
    fi
    ERRORFLAG=0
    sleep 2.0    ##        read -p "hit key to proceed"
    for RTR in ${LIST_OF_ROUTERS[@]}; do
        ##only use $RTR if it is the name of a router in the system
        if [[ ${RTR:6:3} == "RTR" ]]; then
            if (( SCRIPT_VERBOSITY > 1 )); 
            then
                echo "Testing link lock state of link L in router $RTR"
            fi
            EXECSTR="caget -t ${RTR}:LOCK_L_RBV"
##            echo "executing $EXECSTR"
            TEST1=$($EXECSTR)
            #the LOCK_L_RBV is the actual LOCK* signal from the DS92LV18 chip,
            #so Off is a value of '0' which means LOCKED.
            if [ "$TEST1" != "Off" ];
            then
                if (( SCRIPT_VERBOSITY > 1 )); 
                then
                    echo "ERROR : Router $RTR Link L is NOT locked"
                fi
               ((ERRORFLAG=ERRORFLAG+1))
            fi    ##end if [ "$TEST1" != "Off" ];
        fi    ##end of if [[ ${RTR:6:3} == "RTR" ]];
    done
    ##--------------------------------
    ## if ERRORFLAG is not zero, abort here.
    ##--------------------------------

    if [ $ERRORFLAG != 0 ]; then
        echo "Stage 3b failure : $ERRORFLAG links not locked"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    fi     
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];    

##------------------------------------------------------
## stage 3C: If there are no hard failures seen by EPICS, check for errors
## reported by the master trigger firmware.  At this state, if the firmware
## believes the links are locked, the state of the link_init machine can be polled.
##
##    The link_init machine state is 0 (PV value is INIT) if reset.
##    Upon enable it quickly marches through states and stops at state 3 (WAIT_LOCK) until
##    it sees that all non-masked links are locked.  If all are locked it then 
##    advances to state 4 (ALL_LOCK).
##    During these states the link_init machine forces the links of the master trigger
##    to be sending only the SYNC pattern.
##
##    In response to the ALL_LOCK state the user then issues the ACK command by 
##    setting the pv ${MT_VME_LEADER}:MTRG:LOCK_ACK and then releasing it.  At this point the link-init
##    state machine advances to state 5 (ACKED).  The machine stays in the ACKED state
##    until any link drops lock, and the firmware is sampling this at 50MHz.  
##
##    Should an error occur, the machine advances to state 6 (ERROR) and stays in that state
##    forever until the state machine is given a retry command or is reset.
##------------------------------------------------------
if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    caput ScriptStage 3.3 >> ${SCRIPT_LOG_FILE}
    if (( SCRIPT_VERBOSITY > 0 )); then
        echo "Stage 3C: Verifying state of master trigger link-init machine"
    fi
    sleep 2.0    ##        read -p "hit key to proceed"
    EXECSTR="caget -t ${MT_VME_LEADER}:MTRG:LINK_INIT_STATE_RBV"
    if (( SCRIPT_VERBOSITY > 1 )); 
    then
        echo "executing $EXECSTR"
    fi
    TEST1=$($EXECSTR)
    if [ "$TEST1" != "ALL_LOCK" ];
    then
        echo "ERROR : Master Trigger Link Init machine error: should be state ALL_LOCK, is in state $TEST1"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    fi    ##end of if [ "$TEST1" != "ALL_LOCK" ];
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];    

##------------------------------------------------------
## Stage 3D: Similar to the link-init logic of the master trigger each router
## implements a firmware monitor of link L's LOCK.  The PV RTRx:LOST_LOCK will be set
## ("ERROR") if the lock has been lost, and it's a sticky bit.  Setting the PV RTRx:SM_LOST_LOCK_RESET
## will clear the error, but if there are transmission problems the LOST_LOCK will get set again.
##
##    The best way to check this is to whack the SM_LOST_LOCK_RESET of every router and then, after
##  a short delay, test all the LOST_LOCK bits.
##------------------------------------------------------

## do the reset whether or not we're checking for errors
caput ScriptStage 3.4 >> ${SCRIPT_LOG_FILE}
if (( SCRIPT_VERBOSITY > 0 )); then
    echo "Stage 3D: Resetting LOST_LOCK status of routers"
fi

sleep 2.0    ##        read -p "hit key to proceed"

for RTR in ${LIST_OF_ROUTERS[@]}; do
    if [[ ${RTR:6:3} == "RTR" ]]; then
        caput -t ${RTR}:SM_LOST_LOCK_RESET 0 >> ${SCRIPT_LOG_FILE}        ##clear it
        sleep 0.5
        caput -t ${RTR}:SM_LOST_LOCK_RESET 1 >> ${SCRIPT_LOG_FILE}        ##set it
        sleep 0.5
        caput -t ${RTR}:SM_LOST_LOCK_RESET 0 >> ${SCRIPT_LOG_FILE}        ##clear it
        sleep 0.5
    fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
done


if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    if (( SCRIPT_VERBOSITY > 1 )); 
    then    
        echo "Stage 3D: Check LOST_LOCK in each router..will pause here for a second to allow EPICS update of LOST_LOCK bits"
    fi
    sleep 5.0
    if (( SCRIPT_VERBOSITY > 1 )); 
    then    
        echo "Stage 3D: Pause over, now checking LOST_LOCK bits"
    fi
    ERRORFLAG=0
    for RTR in ${LIST_OF_ROUTERS[@]}; do
        if [[ ${RTR:6:3} == "RTR" ]];
            then
            EXECSTR="caget -t ${RTR}:LOST_LOCK_RBV"
            if (( SCRIPT_VERBOSITY > 1 )); 
            then    
                echo "executing $EXECSTR"
            fi
            TEST1=$($EXECSTR)
            if [ "$TEST1" == "ERROR" ]; then
                echo "ERROR : Router $RTR link L lost lock flag set after being reset"
                ((ERRORFLAG=ERRORFLAG+1))
            fi    ##end of if [ "$TEST1" != "ERROR" ];
        fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
    done    ##end for RTR in ${LIST_OF_ROUTERS[@]}; do
    if [ $ERRORFLAG != 0 ]; then
        echo "Stage 3D failure : $ERRORFLAG links report lost lock"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    fi    ##end  if [ $ERRORFLAG != 0 ]; then
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];    
##=================================================================================================================================
##    At this point the expectation is that the master trigger is driving SYNC to all router triggers and that
##    all router triggers are driving SYNC to the master trigger, and all links that should be locked, are.
##    All clocks are local, there has been no switching of the clock, and no "data" is being transferred between
##    master trigger and routers.  We have just verified that all the connections work when sending the SYNC (50MHz clock)
##    in both directions.
##
##    Now the routers must be switched to use the clock from the trigger, and the master switched from sending SYNC
##  to the TTCL format, and we see what happens.  Clock switch must occur before data format switch, or else routers
##  will guaranteed have issues.
##=================================================================================================================================


##------------------------------------------------------
## Stage 3E: Flip the routers from using local clock to link clock, 
## see what breaks.
##------------------------------------------------------
caput ScriptStage 3.5 >> ${SCRIPT_LOG_FILE}
if (( SCRIPT_VERBOSITY > 0 )); 
then
    echo "Stage 3E: Flip routers to use link clock instead of local clock, then re-test routers"
fi

sleep 2.0    ##        read -p "hit key to proceed"

for RTR in ${LIST_OF_ROUTERS[@]}; do
    if [[ ${RTR:6:3} == "RTR" ]]; then
        caput -t ${RTR}:ClkSrc 1 >> ${SCRIPT_LOG_FILE}        ##Change clock source from local to link
    fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
done

sleep 1.0
## switching the clock source in the routers is also quite certain to cause the master trigger
## link-init machine to have an error, so reset that too.

caput -t ${MT_VME_LEADER}:MTRG:RESET_LINK_INIT 1 >> ${SCRIPT_LOG_FILE}        ##turn reset on
caput -t ${MT_VME_LEADER}:MTRG:LOCK_RETRY 0 >> ${SCRIPT_LOG_FILE}            ##ensure related controls off
caput -t ${MT_VME_LEADER}:MTRG:LOCK_ACK 0 >> ${SCRIPT_LOG_FILE}
sleep 2.0
caput -t ${MT_VME_LEADER}:MTRG:RESET_LINK_INIT 0 >> ${SCRIPT_LOG_FILE}        ##turn reset off
sleep 2.0


##switching the clock source is certain to cause a Link L lost lock error in the routers,
##but it should be momentary.  So we clear the error, wait a second, then test.
for RTR in ${LIST_OF_ROUTERS[@]}; do
    if [[ ${RTR:6:3} == "RTR" ]]; then
        caput -t ${RTR}:SM_LOST_LOCK_RESET 0 >> ${SCRIPT_LOG_FILE}        ##clear it
        sleep 0.5
        caput -t ${RTR}:SM_LOST_LOCK_RESET 1 >> ${SCRIPT_LOG_FILE}        ##set it
        sleep 0.5
        caput -t ${RTR}:SM_LOST_LOCK_RESET 0 >> ${SCRIPT_LOG_FILE}        ##clear it
        sleep 0.5
    fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
done



##check that nobody dropped the ball after switching clock source

if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then

    sleep 5.0
    ERRORFLAG=0
    for RTR in ${LIST_OF_ROUTERS[@]}; do
        if [[ ${RTR:6:3} == "RTR" ]];
            then
            EXECSTR="caget -t ${RTR}:LOST_LOCK_RBV"
            if (( SCRIPT_VERBOSITY > 1 )); 
            then    
                echo "executing $EXECSTR"
            fi
            TEST1=$($EXECSTR)
            if [ "$TEST1" == "ERROR" ]; then
                echo "ERROR : Router $RTR link L lost lock flag set after switching clock source"
                ((ERRORFLAG=ERRORFLAG+1))
            fi    ##end of if [ "$TEST1" != "ERROR" ];
        fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
    done    ##end for RTR in ${LIST_OF_ROUTERS[@]}; do
    if [ $ERRORFLAG != 0 ]; then
        echo "Stage 3E failure : $ERRORFLAG links report lost lock"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    fi    ##end  if [ $ERRORFLAG != 0 ]; then

fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];



##------------------------------------------------------
## Stage 3F: Release the Sync control from master trigger to routers
## by ACKing the link-init state machine.  Issue Imperative Sync and
## clear router diagnostic counters.
##------------------------------------------------------
caput ScriptStage 3.6 >> ${SCRIPT_LOG_FILE}
if (( SCRIPT_VERBOSITY > 0 )); then
    echo "Stage 3F: ACK master trigger link-init, issue Imp Sync, clear router counters"
fi

sleep 2.0    ##        read -p "hit key to proceed"

caput -t ${MT_VME_LEADER}:MTRG:LOCK_RETRY 1 >> ${SCRIPT_LOG_FILE}
        sleep 0.5
caput -t ${MT_VME_LEADER}:MTRG:LOCK_RETRY 0 >> ${SCRIPT_LOG_FILE}    ##pulse the retry
        sleep 0.5
##re-re-reset the lost-lock in each router
for RTR in ${LIST_OF_ROUTERS[@]}; do
    if [[ ${RTR:6:3} == "RTR" ]]; then
        caput -t ${RTR}:SM_LOST_LOCK_RESET 0 >> ${SCRIPT_LOG_FILE}        ##clear it
        sleep 0.5
        caput -t ${RTR}:SM_LOST_LOCK_RESET 1 >> ${SCRIPT_LOG_FILE}        ##set it
        sleep 0.5
        caput -t ${RTR}:SM_LOST_LOCK_RESET 0 >> ${SCRIPT_LOG_FILE}        ##clear it
        sleep 0.5
    fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
done
caput -t ${MT_VME_LEADER}:MTRG:LOCK_ACK 1 >> ${SCRIPT_LOG_FILE}
        sleep 0.5
caput -t ${MT_VME_LEADER}:MTRG:LOCK_ACK 0 >> ${SCRIPT_LOG_FILE}    ##pulse the ACK
        sleep 0.5

caput -t ${MT_VME_LEADER}:MTRG:IMP_SYNC 1 >> ${SCRIPT_LOG_FILE}  ##turn on the IMP_SYNC, leave on while checking master status.
for RTR in ${LIST_OF_ROUTERS[@]}; do
    if [[ ${RTR:6:3} == "RTR" ]]; then
        caput -t ${RTR}:CLEAR_DIAG_COUNTERS 1 >> ${SCRIPT_LOG_FILE}        ##this is a write to a pulsed control, but EPICS is dumb, so

        sleep 0.5

        caput -t ${RTR}:CLEAR_DIAG_COUNTERS 0 >> ${SCRIPT_LOG_FILE}        ##you are forced to write twice.

        sleep 0.5

    fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
done

##check that nobody dropped the ball after switching master trig from SYNC to data

if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    sleep 2.0
    ERRORFLAG=0
    for RTR in ${LIST_OF_ROUTERS[@]}; do
        if [[ ${RTR:6:3} == "RTR" ]];
            then
            EXECSTR="caget -t ${RTR}:LOST_LOCK_RBV"
            if (( SCRIPT_VERBOSITY > 1 )); 
            then    
                echo "executing $EXECSTR"
            fi
            TEST1=$($EXECSTR)
            if [ "$TEST1" == "ERROR" ]; then
                echo "ERROR : Router $RTR link L lost lock flag set after switching from SYNC to TTCL"
                ((ERRORFLAG=ERRORFLAG+1))
            fi    ##end of if [ "$TEST1" != "ERROR" ];
        fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
    done    ##end for RTR in ${LIST_OF_ROUTERS[@]}; do
    if [ $ERRORFLAG != 0 ]; then
        echo "Stage 3F failure : $ERRORFLAG links report lost lock"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    fi    ##end  if [ $ERRORFLAG != 0 ]; then

##also check that master trigger is happy after the ACK
    if (( SCRIPT_VERBOSITY > 1 )); then
    echo "Stage 3F: Verifying state of master trigger link-init machine"
    fi
    EXECSTR="caget -t ${MT_VME_LEADER}:MTRG:LINK_INIT_STATE_RBV"
##    echo "executing $EXECSTR"
    TEST1=$($EXECSTR)
    if [ "$TEST1" != "ACKED" ];
    then
        echo "ERROR : Master Trigger Link Init machine error: should be state ACKED, is in state $TEST1"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    fi    ##end of if [ "$TEST1" != "ACKED" ];
fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];

##------------------------------------------------------
## Stage 3G: clear router diagnostic counters, wait a couple seconds,
## verify that counter 6 (count of receiver state machine errors) and
## counter 7 (count of physical lost-lock from SERDES chip) both stay zero.
##------------------------------------------------------
caput ScriptStage 3.7 >> ${SCRIPT_LOG_FILE}
if (( SCRIPT_VERBOSITY > 0 )); then
    echo "Stage 3G: Verifying stability of trigger system..this will take a few seconds"
fi

sleep 2.0    ##        read -p "hit key to proceed"

for RTR in ${LIST_OF_ROUTERS[@]}; do
    if [[ ${RTR:6:3} == "RTR" ]]; then
        caput -t ${RTR}:CLEAR_DIAG_COUNTERS 1 >> ${SCRIPT_LOG_FILE}        ##this is a write to a pulsed control, but EPICS is dumb, so
        sleep 0.5
        caput -t ${RTR}:CLEAR_DIAG_COUNTERS 0 >> ${SCRIPT_LOG_FILE}        ##you are forced to write twice.
        sleep 0.5
    fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
done

sleep 15.0

if [ $PERFORM_ERROR_CHECKS != 0 ];        ##if PERFORM_ERROR_CHECKS is nonzero, perform the checks.
    then
    ERRORFLAG=0
    for RTR in ${LIST_OF_ROUTERS[@]}; do
        if [[ ${RTR:6:3} == "RTR" ]];
            then
            EXECSTR="caget -t ${RTR}:Diag_F_RBV"        ##Diag counter F is "Router lock count"
            if (( SCRIPT_VERBOSITY > 1 )); 
            then    
                echo "executing $EXECSTR"
            fi
            TEST1=$($EXECSTR)
            if [ "$TEST1" != 0 ]; then
                echo "ERROR : Router $RTR State machine lock count not zero ($TEST1) : system not stable"
                ((ERRORFLAG=ERRORFLAG+1))
            fi    ##end of if [ "$TEST1" != 0 ];
        fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
    done    ##end for RTR in ${LIST_OF_ROUTERS[@]}; do

    for RTR in ${LIST_OF_ROUTERS[@]}; do
        if [[ ${RTR:6:3} == "RTR" ]];
            then
            EXECSTR="caget -t ${RTR}:Diag_G_RBV"        ##Diag counter G is "SERDES chip lock count"
            if (( SCRIPT_VERBOSITY > 1 )); 
            then    
                echo "executing $EXECSTR"
            fi
            TEST1=$($EXECSTR)
            if [ "$TEST1" != 0 ]; then
                echo "ERROR : Router $RTR Link L SERDES chip lock count not zero ($TEST1) : system not stable"
                ((ERRORFLAG=ERRORFLAG+1))
            fi    ##end of if [ "$TEST1" != 0 ];
        fi    ##end if [[ ${RTR:6:3} == "RTR" ]];
    done    ##end for RTR in ${LIST_OF_ROUTERS[@]}; do

    if [ $ERRORFLAG != 0 ]; then
        echo "Stage 3G failure : $ERRORFLAG links report lost lock"
        caput Setup_Script_State 4 >> ${SCRIPT_LOG_FILE}        ##sets PV displaying setup state to error condition
        caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}
        exit 1
    else
        if (( SCRIPT_VERBOSITY > 1 )); then
            echo "Stage 3G success!  Trigger system links all stable."
        fi
    fi    ##end  if [ $ERRORFLAG != 0 ]; then

fi    ##end of if [ $PERFORM_ERROR_CHECKS != 0 ];



exit 0
