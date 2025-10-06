
################################################
##   Ryan20250905:
##
##   SLOT  Board  DEVICE
##   1            IOC
##   2            empty
##   3     0      MDIG1
##   4     1      MDIG2
##   5     2      MDIG3
##   6     3      MDIG4
##   7            empty
################################################

ProgramFlash(0, 0, "BUS_LEFT.bin")
taskDelay(100)
ConfigureFlash(0, 0)
taskDelay(100)

ProgramFlash(1, 0, "BUS_LEFT.bin")
taskDelay(100)
ConfigureFlash(1, 0)
taskDelay(100)

ProgramFlash(2, 0, "BUS_LEFT.bin")
taskDelay(100)
ConfigureFlash(2, 0)
taskDelay(100)

ProgramFlash(3, 0, "BUS_LEFT.bin")
taskDelay(100)
ConfigureFlash(3, 0)
taskDelay(100)


#---- repeat configure to make sure it configure
ConfigureFlash(0, 0)
taskDelay(100)
ConfigureFlash(1, 0)
taskDelay(100)
ConfigureFlash(2, 0)
taskDelay(100)
ConfigureFlash(3, 0)
taskDelay(100)

