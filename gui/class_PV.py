import epics
import time

class PV():

  def __init__(self):
    self.Clear()

  def Clear(self):
    self.name = ""
    self.RBV_exist = False
    self.ReadONLY = False
    self.States = []
    self.value = None
    self.char_value = ""

    self.isUpdated = False

  def SetName(self, name):
    self.name = name

  def SetRBVExist(self, rbv: bool):
    self.RBV_exist = rbv

  def SetReadONLY(self, ro: bool):
    self.ReadONLY = ro

  def AddState(self, state_str):
    self.States.append(state_str)

  def AddCallback(self):
    if self.RBV_exist:
      p = epics.PV(self.name+"_RBV")
    else:
      p = epics.PV(self.name)
    
    p.add_callback(self.on_change)

  def SetFullPV(self, name,  ro, rbv, states):
    self.name = name
    self.ReadONLY = ro
    self.RBV_exist = rbv
    self.States = states
    self.AddCallback()

  def NumStates(self) -> int:
    return len(self.States)

  def SetValue(self, value, sync = False, debug=True):
    if self.ReadONLY:
      return
    
    self.value = value
    p = epics.PV(self.name)
    p.put(value, wait=sync)

    self.value = p.value
    self.char_value = p.char_value
    if debug:
      print(f"PV::SetValue() {self.name} now is {self.value}, {self.char_value}")
 

  def GetValue(self, fromEPICS=False) -> str:
    if fromEPICS:
      if self.RBV_exist:
        p = epics.PV(self.name+"_RBV")
      else:
        p = epics.PV(self.name)
      self.value = p.get()
      self.char_value = p.char_value

    else:
      return self.char_value
    self.isUpdated = False
    
  def on_change(self, **kw):
    self.value = kw['value']
    # self.char_value = kw['char_value']
    self.isUpdated = True

    # print(f"{self.name} changed to {self.value}, {self.isUpdated}")

  def __str__(self):
    return f"PV({self.name:40s}, ReadOnly={self.ReadONLY}, RBV_exist={self.RBV_exist}, States={self.States})"