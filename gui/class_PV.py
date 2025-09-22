import epics
import time

class PV():
  def __init__(self):
    self.Clear()

  def Clear(self):
    self.name = ""
    self.ReadOnly = False
    self.Type = ""
    self.States = []
    self.value = None
    self.char_value = ""

  def SetName(self, name):
    self.name = name

  def SetReadOnly(self, ro: bool):
    self.ReadOnly = ro

  def SetType(self, type_str):
    self.Type = type_str

  def AddState(self, state_str):
    self.States.append(state_str)

  def SetFullPV(self, name, type_str, ro, states):
    self.name = name
    self.Type = type_str
    self.ReadOnly = ro
    self.States = states

  def NumStates(self) -> int:
    return len(self.States)

  def SetValue(self, value, sync = False):
    if self.ReadOnly:
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
      p = epics.PV(self.name+"_RBV")
      self.value = p.get()
      self.char_value = p.char_value
    else:
      return self.char_value
    
  def __str__(self):
    return f"PV({self.name:40s}, Type={self.Type:3s}, ReadOnly={self.ReadOnly:d}, States={self.States})"