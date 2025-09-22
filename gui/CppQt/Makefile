EPICS_BASE ?= /path/to/epics-base
EPICS_HOST_ARCH ?= linux-x86_64

CXX = g++

testing: test.cpp class_PV.h
	$(CXX) test.cpp -o test \
			-I$(EPICS_BASE)/include \
			-I$(EPICS_BASE)/include/os/Linux\
			-I$(EPICS_BASE)/include/compiler/gcc/ \
			-L$(EPICS_BASE)/lib/$(EPICS_HOST_ARCH) \
			-lca -lCom

.PHONY: clean
clean:
	rm -f testing