#!/bin/bash -l

## created by Ryan at 20250730

EDMSCRIPTS=/global/ioc/gui/scripts
SYSTEM_DEFINE_FILE="./VME99_SYSTEM_DEFINES.sh"
SYSTEM_CONFIG_FILE="./VME99_CONFIG.sh"

echo "SERDES_DIG_TRIG starting at ${EDMSCRIPTS}"
cd ${EDMSCRIPTS}

echo "Loading system parameters from ${SYSTEM_DEFINE_FILE}"
source ./VME99_SYSTEM_DEFINES.sh

echo "Loading system configuration from ${SYSTEM_CONFIG_FILE}"
source ./VME99_CONFIG.sh

source Serdes_Linkup.sh ${SYSTEM_CONFIG_FILE} ${EDMSCRIPTS}

