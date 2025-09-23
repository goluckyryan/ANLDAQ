from class_PV import PV
from copy import copy

class DIG():
  def __init__(self):
    self.Clear()

  def Clear(self):
    self.CH_PV = []
    self.VME_name = ""
    self.Dig_name = ""
    self.NumChannels = 10

    self.CH_PV = None  # CH_PV[channel][pv_index]

  def SetBoardID(self, vme_name, dig_name):
    self.VME_name = vme_name
    self.Dig_name = dig_name

  def SetCH_PV(self, ch_pv_list):
    # Ensure CH_PV is a 2D array with NumChannels rows
    self.CH_PV = [[] for _ in range(self.NumChannels)]
    for i in range(self.NumChannels):

      for pv in ch_pv_list:
        pv_ch = copy(pv)
        pv_ch.SetName(f"{self.VME_name}:{self.Dig_name}:{pv.name}{i}")
        self.CH_PV[i].append(pv_ch)

  def SetBoard_PV(self, board_pv):
    self.Board_PV = []
    for pv in board_pv:
      pv_b = copy(pv)
      pv_b.SetName(f"{self.VME_name}:{self.Dig_name}:{pv.name}")
      self.Board_PV.append(pv_b)
  
  def UpdateAllPVs(self):
    for i in range(self.NumChannels):
      for pv in self.CH_PV[i]:
        pv.GetValue(fromEPICS=True)
    for pv in self.Board_PV:
      pv.GetValue(fromEPICS=True)