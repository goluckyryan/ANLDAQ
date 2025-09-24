import epics
import time

class PV():

  def __init__(self):
    self.Clear()

  def Clear(self):
    self.name = ""
    self.RBV_exist = False
    self.Type = ""
    self.States = []
    self.value = None
    self.char_value = ""

    self.isUpdated = False

  def SetName(self, name):
    self.name = name

  def SetRBVExist(self, ro: bool):
    self.RBV_exist = ro

  def SetType(self, type_str):
    self.Type = type_str

  def AddState(self, state_str):
    self.States.append(state_str)

  def AddCallback(self):
    if self.RBV_exist:
      p = epics.PV(self.name+"_RBV")
    else:
      p = epics.PV(self.name)    
    p.add_callback(self.on_change)

  def SetFullPV(self, name, type_str, ro, states):
    self.name = name
    self.Type = type_str
    self.RBV_exist = ro
    self.States = states
    self.AddCallback()

  def NumStates(self) -> int:
    return len(self.States)

  def SetValue(self, value, sync = False):
    if self.RBV_exist:
      return
    
    if isinstance(value, str):
      self.char_value = value
    else:   
      value = value
    p = epics.PV(self.name)
    p.put(value, wait=sync)

    if isinstance(value, str):
      self.value = p.value
    else:
      self.char_value = p.char_value
 

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
    return f"PV({self.name:40s}, Type={self.Type:3s}, RBV_exist={self.RBV_exist:d}, States={self.States})"