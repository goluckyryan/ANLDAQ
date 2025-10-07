#!/bin/bash -l

cd ${2}		##2nd arg to this is the path to scripts ($EDMSCRIPTS)



#####################################################################
#
#   THIS IS THE GENERIC TRIGGER SETUP SCRIPT THAT IS INDEPENDENT OF SYSTEM CONFIGURATION
#
##	THINGS YOU NEED TO KNOW
##
##	1) IN THE EPICS SETUP, WRITING TO A WHOLE REGISTER WILL NOT CHANGE THE VALUE
##		OF ANY BREAKOUT PVs ASSOCIATED WITH THAT REGISTER.  
##			Example:  There's a PV VME10:MTRG:reg_INPUT_LINK_MASK that has a 'readback'
##					  PV named VME10:MTRG_reg_INPUT_LINK_MASK_RBV.If you write a value
##					  to the reg_INPUT_LINK_MASK process variable, the _RBV gets what you wrote.
##					  HOWEVER, there are a bunch of 'breakout' PVs named VME10:MTRG:ILM_A through VME10:MTRG:ILM_H
##					  that map to bits 0 to 7 of the reg_INPUT_LINK_MASK. WRITING TO THE REGISTER DOES NOT
##					  UPDATE THE 'breakout' PROCESS VARIABLES, SO THEY ARE WRONG AFTER WRITING TO THE REGISTER.
##
##		a) Writing (setting) the 'breakout' PVs writes to the register, to the reg_INPUT_LINK_MASK_RBV will change,
##		   BUT THE reg_INPUT_LINK_MASK process variable DOES NOT CHANGE.
##
##				--THIS IS BECAUSE THE 'breakout' PROCESS VARIABLE USES A DIFFERENT PV TO DO ITS REGISTER WRITE
##				  THAN THE reg_ PV.
##
##		b) Since the user control windows all use 'breakout' PVs and not 'whole reg' PVs, DESPITE EFFICIENCY LOSSES
##		   EVERYTHING IN THE SCRIPT SHOULD USE 'breakout' PVs.
#####################################################################

#####################################################################
##	EDIT LOG
##
##	20220906: split this big script into subsidiary scripts.
##	20230331: moved this and its subscripts to /global/ioc/gui/scripts.  Modified files to match new system wiring.
#####################################################################


##===================================================================
## System definition area
##
##	Bash variables define how many boards are connected where.
##===================================================================
echo "Loading system parameters from DGS_SYSTEM_DEFINES.sh"
source ./VME99_SYSTEM_DEFINES.sh

if [ -z "$1" ];		##test for no argument specified.
	then
	echo "no configuration file specified, defaulting to DGS_CONFIG.sh"
	SYSTEM_CONFIG_FILE="./VME99_CONFIG.sh"
else
	echo "Using specified configuration file $1"
	SYSTEM_CONFIG_FILE=$1
fi

source ./${SYSTEM_CONFIG_FILE}


if [ -z "${SCRIPT_LOG_FILE}" ];		##test for non-specification of redirection string
	then
	echo "script log file defined as ${SCRIPT_LOG_FILE}, set to ${SCRIPT_LOG_FILE}"
	SCRIPT_LOG_FILE="${SCRIPT_LOG_FILE}"
fi

## This echo ensures that the script log file is opened in addition to providing a header.
## all other redirects are ">>" to append in this and all subsidiary files.
echo "Trigger linkup script started" > ${SCRIPT_LOG_FILE}


caput Setup_Script_State 7 >> ${SCRIPT_LOG_FILE}		##sets PV displaying setup state to SCRIPT_RUNNING
caput ScriptStage 0 >> ${SCRIPT_LOG_FILE}				##sets PV displaying setup stage to 0


##==================================================================
##	PROGRAMMING HINTS AT END OF THIS FILE INCLUDING USEFUL TEMPLATES
##==================================================================



##===================================================================
##	STAGE 1: set up master trigger to be driving Sync pattern out all links.
##
##	The general assumption at this point is that the user has intentionally and with
##	malice aforethought mangled the setup of the board to maximum degree.
##===================================================================

./trig_setup_Stage1.sh $SYSTEM_CONFIG_FILE ${2}
if [ $? != 0 ]; then
	echo "trig setup Stage 1 failure"
	caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}					##error halt, so stage is set to -1
	exit
fi


##===================================================================
##  STAGE 2: Initialize Routers to receive data from master and send SYNC back to master.
##	During stage 2 all Routers use their local clock and do not attempt to use the clock
##  from the master trigger.
##===================================================================

./trig_setup_Stage2.sh $SYSTEM_CONFIG_FILE ${2}
if [ $? != 0 ]; then
	echo "trig setup Stage 2 failure"
	caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}					##error halt, so stage is set to -1
	exit
fi


##===================================================================
##	STAGE 3: with all trigger boards turned on, all links set up and all drivers enabled,
##	read and check the lock status of all active links.  
##
##	exit if any link that should be locked is not.
##===================================================================

./trig_setup_Stage3.sh $SYSTEM_CONFIG_FILE ${2}
if [ $? != 0 ]; then
	echo "trig setup Stage 3 failure"
	caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}					##error halt, so stage is set to -1
	exit
fi


##===================================================================
##	STAGE 4: Set up all links in digitizers to be sending SYNC to Router
##	and verify that Router sees lock in all enabled links.
##===================================================================

./trig_setup_Stage4.sh $SYSTEM_CONFIG_FILE ${2}
if [ $? != 0 ]; then
	echo "trig setup Stage 4 failure"
	caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}					##error halt, so stage is set to -1
	exit
fi

##===================================================================
##	STAGE 5: Flip digitizers and routers, in order, from sending
##	SYNC to sending "real" data. Check at each step that nothing
##	erroneous occurs.
##===================================================================
./trig_setup_Stage5.sh $SYSTEM_CONFIG_FILE ${2}
if [ $? != 0 ]; then
	echo "trig setup Stage 5 failure"
	caput ScriptStage -1 >> ${SCRIPT_LOG_FILE}					##error halt, so stage is set to -1
	exit
fi

echo ""
echo "********************************************"
echo "trigonly_setup Script Complete"
echo "********************************************"
echo ""
caput Setup_Script_State 1 >> ${SCRIPT_LOG_FILE}				##sets PV displaying setup state to 1 (trig ok)
caput ScriptStage 0 >> ${SCRIPT_LOG_FILE}						##no error, so stage is set to 0



echo "*******************************************************"
echo " This script removes any Link L F1 propagation to ensure"
echo " linkup of the local system it is running in.  Cross-system"
echo " clock/triggering must be reconstituted AFTER this script"
echo " has completed."
echo "*******************************************************"

echo ""
echo ""
echo "***************************************************************"
echo "Trigger linkup script is finished!!!!!!"
echo "***************************************************************"
echo ""
echo ""
exit 0
##=================================================================================================================================
##	END OF ACTIVE CODE		END OF ACTIVE CODE		END OF ACTIVE CODE		END OF ACTIVE CODE
##=================================================================================================================================


##==========================================================================
##	PROGRAMMING TEMPLATES YOU WANT TO USE
##
##	Code below this line is TEMPLATE code, that SHOULD NOT RUN.
##	That's why there is an 'exit' at the start of this block.
##==========================================================================
exit

## really, nothing below this should execute, these are EXAMPLES for you to
## copy and paste from

##---------------------------------------------------
##  This is the generic template for looping over all links
##	that are in use within the master trigger to set something.
##---------------------------------------------------
MASK_FLAG=1
echo "setting master Input Link Mask"
for MT_LINK in ${MT_LINK_MAP[@]}; do
	if [ ${#MT_LINK} != 1 ]; then	##if string length is >1 then we set or clear MASK_FLAG.
		if [ ${MT_LINK} == "MASKED" ]; then
##			echo "Setting mask flag 1 because link name is ${MT_LINK}; length is ${#MT_LINK}"
			MASK_FLAG=1
		else
##			echo "Setting mask flag 0 because link name is ${MT_LINK}; length is ${#MT_LINK}"
			MASK_FLAG=0
		fi
	
	##If, however, the string length is 1 we assume it is a "link name" so tied to a PV name
	else
## use caput as formed below to set all masked links to 1, and set all unmasked links to 0.	
##		caput -t VME10:MTRG:ILM_${MT_LINK} ${MASK_FLAG} >> scr.txt 	#masked links have mask of 1
	fi
done

##---------------------------------------------------
##  This is the generic template for looping over all links
##	that are in use within the master trigger to test something.
##---------------------------------------------------
for MT_LINK in ${MT_LINK_MAP[@]}; do
	if [ ${#MT_LINK} != 1 ]; then	##if string length is >1 then we set or clear MASK_FLAG.
		if [ ${MT_LINK} == "MASKED" ]; then
			MASK_FLAG=1
		else
			MASK_FLAG=0
		fi	##end of 	if [ ${MT_LINK} == "MASKED" ]; 
		
	##else case executes if length of string is 1, and thus must be a link name
	else
		if [ $MASK_FLAG == 0 ]; then
			echo "Testing link lock state of unmasked link ${MT_LINK}"
				EXECSTR="caget -t VME10:MTRG:LOCK_${MT_LINK}_RBV"
				echo "executing $EXECSTR"
				TEST1=$($EXECSTR)
				#the LOCK_L_RBV is the actual LOCK* signal from the DS92LV18 chip,
				#so Off mans '0' which means LOCKED.
				if [ "$TEST1" != "Off" ];
				then
				   echo "ERROR : Master Trigger Link $MT_LINK is NOT locked"
				   ((ERRORFLAG=ERRORFLAG+1))
				fi	##end if [ "$TEST1" != "Off" ];
		fi	##end of if [ $MASK_FLAG == 0 ]
	fi	##end of if [ ${#MT_LINK} != 1 ];
done	

##---------------------------------------------------
##	This is the template for looping over all used channels of a router
##---------------------------------------------------
for RTR in ${LIST_OF_ROUTERS[@]}; do
	#-------------------------------------------------------------------
	#  Router board-level setups inside this if clause, because string is of form "RTRx"
	#-------------------------------------------------------------------
	if [[ ${RTR:0:3} == "RTR" ]];
		then
		RTRNAME=$RTR	##save router name for when we're cycling through the links
		RTR_LINKIDX=0
	#-------------------------------------------------------------------
	#  Router channel-level setups inside this if clause, so ${RTR} will be the link letter
	#-------------------------------------------------------------------
	else
		##-------------------------------------------------------------------
		## if $RTR is "X", this is an unused channel
		##-------------------------------------------------------------------
		if [ $RTR == "X" ];	
		then				
			## do what you want to do for an unused link
		    ((RTR_LINKIDX=RTR_LINKIDX+1))
		##-------------------------------------------------------------------
		## if $RTR is not "X", this is an active channel, so $RTR is a letter (A, B, C, etc.) and can be used directly
		##-------------------------------------------------------------------
		else
			## do what you want to do for a link that is in use
		    ((RTR_LINKIDX=RTR_LINKIDX+1))
		fi
	fi
done
