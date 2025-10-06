## go to the FW directory

cd "/dk/fs2/dgs/global_32/ioc/FW_Maint"


################################################
##   JTA20230331:
##
##   SLOT  Board  DEVICE
##   1            IOC
##   2     0      MTRG
##   3     1      RTRG
##   4            empty
##   5            empty
##   6            empty
##   7            empty
################################################

ProgramFlash(0, 0, "trigger_top.bin")
taskDelay(100)
ConfigureFlash(0, 0)
taskDelay(100)

ProgramFlash(1, 0, "V4747_mod_router_top.bin")
taskDelay(100)
ConfigureFlash(1, 0)
taskDelay(100)

#---- repeat configure to make sure it configure
ConfigureFlash(0, 0)
taskDelay(100)
ConfigureFlash(1, 0)
taskDelay(100)

