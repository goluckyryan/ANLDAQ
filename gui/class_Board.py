from class_PV import PV
from copy import copy

class Board():
  def __init__(self):
    self.Clear()

  def Clear(self):
    self.CH_PV = []
    self.BD_name = ""
    self.NumChannels = 0

    self.CH_PV = None  # CH_PV[channel][pv_index]

  def SetBoardName(self, bd_name):
    self.BD_name = bd_name

  def SetCH_PV(self, nCh, ch_pv_list):
    # Ensure CH_PV is a 2D array with NumChannels rows
    self.NumChannels = nCh
    self.CH_PV = [[] for _ in range(self.NumChannels)]
    for i in range(self.NumChannels):

      for pv in ch_pv_list:
        if not isinstance(pv, PV):
          continue

        pv_ch = copy(pv)
        pv_ch.SetName(f"{self.BD_name}:{pv.name}{i}")
        pv_ch.AddCallback()
        self.CH_PV[i].append(pv_ch)

  def SetBoard_PV(self, board_pv):
    self.Board_PV = []
    for pv in board_pv:

      if not isinstance(pv, PV):
        continue

      if pv.name.endswith("LiveTS"):
        continue
      
      pv_b = copy(pv)
      pv_b.SetName(f"{self.BD_name}:{pv.name}")
      pv_b.AddCallback()
      self.Board_PV.append(pv_b)
        
