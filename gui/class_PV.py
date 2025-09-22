class PV():
  def __init__(self):
    self.Clear()

  def Clear(self):
    self.name = ""
    self.ReadOnly = False
    self.Type = ""
    self.States = []
    self.value = None

  def SetName(self, name):
    self.name = name

  def SetReadOnly(self, ro: bool):
    self.ReadOnly = ro

  def SetType(self, type_str):
    self.Type = type_str

  def AddState(self, state_str):
    self.States.append(state_str)

  def NumStates(self):
    return len(self.States)

  def SetValue(self, value):
    self.value = value

  def __str__(self):
    return f"PV({self.name:40s}, Type={self.Type:3s}, ReadOnly={self.ReadOnly:d}, States={self.States})"