###############################################################
## This is the boot script for IOC99 (GRETINA lab test stand)
##
## Stupid things you need to know
##
##		1) EPICS commands like asynxxxxconfig() must be by themselves on 
##		   a line with no following comment, otherwise you get syntax errors.
##
###############################################################

cd "/global/ioc/boot"

# the ports here are defined for use in Digital Gammasphere
#
#       DGS     : 5064/5065
#       DFMA    : 5068/5069
#       Xarray  : 5072/5073
#       G-wing  : 5074/5075
#       F-wing/microball  : 5078/5079
#
putenv("EPICS_CA_SERVER_PORT = 5074")
putenv("EPICS_CA_REPEATER_PORT = 5075")
putenv("EPICS_CA_CONN_TMO = 40")
putenv("EPICS_CA_BEACON_PERIOD = 2")

# load files containing semi-useful shell commands and paths
< cdCommandsLab
taskDelay(100)
< nfsCommands
taskDelay(100)

# load the binary image file containing the EPICS tasks and the readout tasks
# inLoop, outLoop and MiniSender.

cd topbin
pwd
ld < gretDet.munch
taskDelay(100)


# gretDet.dbd is the DataBaseDefinition file that enumerates the DTYPs (data types) used by all the
# EPICS databases that will be loaded in following lines.
cd top
pwd

dbLoadDatabase("dbd/gretDet.dbd",0,0)
taskDelay(100)

gretDet_registerRecordDeviceDriver(pdbbase)
taskDelay(100)

putenv("EPICS_TS_MIN_WEST=360")

################################################
##	JTA20230508:
##
##	SLOT		DEVICE
##	1			IOC
##	2			MDIG1
##	3			empty
##	4			Digitizer Tester
##	5			empty
##	6			RTR1
##	7			MTRG
################################################

### When loading databases we use a taskDelay() call to pause momentarily in case
### the load of the databases throws errors.  If that is not done the error messages
### get lost in the echo of other commands being executed because the dbLoadRecords()
### command returns control to the shell BEFORE THE RECORDS IN THE DATABASE ARE READ.

########## Load EPICS databases for register-level PVs of modules within this crate
##
## The 'CRATE' and 'BOARD' substitutions are used in forming PV names such as
## record(longin,"VME$(CRATE):$(BOARD):reg_SKEW_CTL_A_RBV")
##
## so CRATE is generally a number and BOARD is generally "MTRG", "RTRx", "MDIGx" or "SDIGx"
##
## The BOARD argument in these lines must be identical to the PortName (first argument) of
## the associated asynDigitizerConfig(), asynTrigMasterConfig1() or asynTrigRouterConfig1()
## lines following this database block.
##
dbLoadRecords("db/MTrigRegisters.template",   "CRATE=99,BOARD=MTRG")
dbLoadRecords("db/RTrigRegisters.template",   "CRATE=99,BOARD=RTR1")
dbLoadRecords("db/MDigRegisters.template",    "CRATE=99,BOARD=MDIG1")
dbLoadRecords("db/MDigRegisters.template",    "CRATE=99,BOARD=MDIG2")
taskDelay(100)

########## Load EPICS databases for field-of-register-level PVs of modules within this crate
dbLoadRecords("db/MTrigUser.template",        "CRATE=99,BOARD=MTRG")
dbLoadRecords("db/RTrigUser.template",        "CRATE=99,BOARD=RTR1")
dbLoadRecords("db/MDigUser.template",         "CRATE=99,BOARD=MDIG1")
dbLoadRecords("db/MDigUser.template",         "CRATE=99,BOARD=MDIG2")
taskDelay(100)

########## Load EPICS databases for VME FPGA register-level PVs of modules within this crate
dbLoadRecords("db/MDigRegistersVME.template",    "CRATE=99,BOARD=MDIG1")
dbLoadRecords("db/MDigRegistersVME.template",    "CRATE=99,BOARD=MDIG2")
taskDelay(100)

########## Load EPICS databases for VME FPGA field-of-register-level PVs of modules within this crate
dbLoadRecords("db/MDigUserVME.template",         "CRATE=99,BOARD=MDIG1")
dbLoadRecords("db/MDigUserVME.template",         "CRATE=99,BOARD=MDIG2")
taskDelay(100)


########## Load EPICS database of generic debugging PVs (peek/poke)
## For the debug PVs, additional parameters are required, and the BOARD is always "DBG" for "debug".
#dbLoadRecords("db/asynDebug.template",        "CRATE=99,BOARD=DBG,ADDR=0,TIMEOUT=1")
#taskDelay(100)

##### Load EPICS database of per-slot readout enable process variables; required in every crate that does readout.
dbLoadRecords("db/daqSegment2.template",      "CRATE=99,BOARD=MTRG")
dbLoadRecords("db/daqSegment2.template",      "CRATE=99,BOARD=MDIG1")
dbLoadRecords("db/daqSegment2.template",      "CRATE=99,BOARD=MDIG2")
taskDelay(100)

##### Load EPICS database of per-crate process variables used by inLoop, outLoop and MiniSender
##    required in every crate that does readout.
##
## Note: previous .cmd files used to invoke a database named "OnMon.template"; this database is completely deprecated
##       and should not be loaded.
dbLoadRecords("db/daqCrate.template","CRATE=99")
taskDelay(100)


##### Load EPICS database of per-crate Global fanout process variables
##    required in every crate that does readout.
##
dbLoadRecords("db/dgsGlobals_DGS_VME99.db","CRATE=99")
taskDelay(100)

############# before loading any board, initialize the DAQ board structure in the driver.
InitializeDaqBoardStructure()

####### Now map the boards in the crate between name, arbitrary board number and physical slot in crate #####################
# Need to give (const char *portName, int board_number, int slot)  
# the Board # is defined as
#     MDIG1, irrespective of slot, is Board # 0
#     SDIG1, irrespective of slot, is Board # 1
#     MDIG2, if present, irrespective of slot, is Board # 2
#     SDIG2, if present, irrespective of slot, is Board # 3
#     Any trigger modules or other non-digitizer modules are assigned Board #s 4,5 or 6.
#

##MDIG1, is Board #0, is in Slot #2
asynDigitizerConfig("MDIG1",0,2)
asynDigitizerConfig("MDIG2",1,4)
##RTR1, is Board #4, is in Slot #6
asynTrigRouterConfig1("RTR1",4,6)
##MTRG, is Board #5, is in Slot #7
asynTrigMasterConfig1("MTRG",5,7)
##digitizer tester, is set up as a 'debug' object, to allow peek/poke through addressing only.  no specific config yet.

####### call a function that initializes the 'debug' screen support #####################
asynDebugConfig("DBG",0)

##(const char *portName, int board_number), but we believe the board_number is meaningless.

cd startup


##################### Run the dreaded iocInit()
iocInit()

dumpFIFO = 0

#New feature for initializing Quueing system
setupFIFOReader()

## Assign user-defined id numbers to each board in crate for later data sorting purposes
## The user package data numbering is four per VME crate, starting with 101-104 in VME01, 105-108 in VME02, etc.
## The formula used to calculate the "user package data" value is 
##      [(VME crate # - 1) * 4] + 101 + (Board#)   where (Board#) is restricted to the set {0,1,2,3} for digitizers
##                                                 as defined above.
##
## The user package data numbering for trigger modules is defined as
##
##		The master trigger is 150.
##		In the future, Router triggers will be RTR1 = 151, RTR2 = 152, etc. for however may routers are in the system.
##		However as of 20230331, Routers have no register to store a package data value.
##

dbpf "VME99:MDIG1:user_package_data","160"
dbpf "VME99:MDIG2:user_package_data","161"
dbpf "VME99:MTRG:USER_PACKAGE_DATA","162"

## and finally, start up the DAQ programs themselves (inLoop, outLoop and MiniSender).
## all three programs require the CRATE number "CRATE" that is the same as the number of the VMExx: identifier.
## Additionally inLoop requires that you pass in the "B" parameters, one per every slot in the crate, using
## then same "R" substitution values as used in the dbLoadRecords commands for every populated slot, and using
## then value "X" in all unpopulated slots.
##
## This will allow inLoop to correctly form the PV names that it will use to monitor control PVs related to which
## boards are to be read out and/or which FIFO of a trigger it will read out.
##
## For example, B3=X will cause inLoop to look for the PV name X_CS_Ena
## 
## 
seq &inLoop,"CRATE=99,B0=MDIG1,B1=MIG2,B2=X,B3=X,B4=X,B5=MTRG,B6=X"
taskDelay(100)
seq &outLoop,"CRATE=99"
taskDelay(100)
seq &MiniSender,"CRATE=99"



