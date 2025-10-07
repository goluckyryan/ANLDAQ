# About

This is font-end repository for the DAQ system using Berkery digitizer.
it has few components:
- **EPICS**: The nerve of the system, communicate all PVs
- **IOC**: The IOC database and munch files
- **GUI**: The graphic user interface 

Since we are using EPICS from the other respository

```sh
git clone <url-of-anldaq-repo>
cd ANLDAQ
git submodule update --init --recursive
```

# Required packages or Library

```sh
apt install python3-pyqt6 python3-pyepics
```


## EPICS

The EPICS can be downloaded from the web, place the base into EPICS folder.

To compile EPICS, just go to EPICS/base-7.0/ and make. no need to set any evirmoment variabel

### SoftIOC

simply go to the directory and make

need to change some configure???

## IOC




## GUI

pyQt6 is being used. In the IOC, edit the bootFiles.txt, put all the boost script into the file, then

```sh
>cd ioc
>./findAllPV.py
```

this will generate All_PV.jason, so that the GUI know how many PV are there.

The entry point is

```sh
>./commander.py
```






