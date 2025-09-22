#include "/home/ryan/ANLDAQ/EPICS/base-7.0/include/cadef.h"
#include <iostream>

class PV {
private:
  std::string pvName;
  chid pvChid;
  double value;

  void Init() {
    pvName = "";
    pvChid = nullptr;
  } 

  bool connect() {
    int status = ca_create_channel(pvName.c_str(), nullptr, nullptr, 0, &pvChid);
    if (status != ECA_NORMAL) {
      std::cerr << "Failed to create channel: " << ca_message(status) << std::endl;
      return false;
    }
    status = ca_pend_io(1.0);
    if (status != ECA_NORMAL) {
      std::cerr << "Channel connect failed: " << ca_message(status) << std::endl;
      return false;
    }
    return true;
  }

public:
  PV(){ Init(); }
  PV(const std::string name) {setName(name);}

  void setName(const std::string name) { 
    pvName = name; 
    connect();
  }

  std::string getName() const { return pvName; }  
  double getValue() const { return value; }

  bool get() {
    int status = ca_get(DBR_DOUBLE, pvChid, &value);
    ca_pend_io(1.0);
    if (status != ECA_NORMAL) {
      std::cerr << "GET failed: " << ca_message(status) << std::endl;
      return false;
    }
    return true;
  }

  bool put(double value) {
    int status = ca_put(DBR_DOUBLE, pvChid, &value);
    ca_pend_io(1.0);
    if (status != ECA_NORMAL) {
      std::cerr << "PUT failed: " << ca_message(status) << std::endl;
      return false;
    }
    get();
    return true;
  }

  ~PV() {
    if (pvChid) ca_clear_channel(pvChid);
  }

};
