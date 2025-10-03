#!/usr/bin/env python3

import sys
import time

from json2pv import GeneratePVLists

DIG_CHANNEL_PV, DIG_BOARD_PV, RTR_BOARD_PV, MTRG_BOARD_PV, DIG_BOARD_LIST, RTR_BOARD_LIST, MTRG_BOARD_LIST = GeneratePVLists('../ioc/All_PV.json')

# exit()

for i, bd in enumerate(DIG_BOARD_LIST):
  print(f"DIG  Board {i:>2d}: {bd}")

for i, bd in enumerate(RTR_BOARD_LIST):
  print(f"RTR  Board {i:>2d}: {bd}")

for i, bd in enumerate(MTRG_BOARD_LIST):
  print(f"MTRG Board {i:>2d}: {bd}")

print("##########################################################################")

from class_Board import Board

DIG_List = []
RTR_List = []

for bd_name in DIG_BOARD_LIST:
  bd = Board()
  bd.SetBoardID(bd_name)
  bd.SetCH_PV(10, DIG_CHANNEL_PV)
  bd.SetBoard_PV(DIG_BOARD_PV)
  DIG_List.append(bd)

for bd_name in RTR_BOARD_LIST:
  bd = Board()
  bd.SetBoardID(bd_name)
  bd.SetBoard_PV(RTR_BOARD_PV)
  RTR_List.append(bd)


MTRG1 = Board()
MTRG1.SetBoardID(MTRG_BOARD_LIST[0])
MTRG1.SetBoard_PV(MTRG_BOARD_PV)

ALLBOARD = DIG_List + RTR_List + [MTRG1]

############################# A GUI window
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QSpinBox, QComboBox, QPushButton
from custom_QClasses import GLabel, GLineEdit, GFlagDisplay, GTwoStateButton
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel

from class_PVWidgets import RTwoStateButton
from class_PV import PV

from gui_Board import BoardPVWindow
from gui_MTRG import MTRGWindow
from gui_RTR import RTRWindow
from gui_DIG import DIGWindow

#^#################################################################################
#^#################################################################################
#^#################################################################################
class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Commander")
    self.setGeometry(1000, 100, 400, 200)

    self.setWindowFlags(
      Qt.WindowType.Window |
      Qt.WindowType.WindowMinimizeButtonHint |
      Qt.WindowType.WindowCloseButtonHint
    )

    self.isACQRunning = False

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    grid_layout = QGridLayout()
    central_widget.setLayout(grid_layout)

    #=============================== GUI setup
    rowIdx = 0

    grid_layout.addWidget(GLabel("Generic Board:"), rowIdx, 0)
    self.comboBox_bd = QComboBox()
    self.comboBox_bd.addItem("Select Board")
    self.comboBox_bd.addItems(DIG_BOARD_LIST)
    self.comboBox_bd.addItems(RTR_BOARD_LIST)
    self.comboBox_bd.addItems(MTRG_BOARD_LIST)
    self.comboBox_bd.setCurrentIndex(0)
    self.comboBox_bd.currentIndexChanged.connect(self.OnGenericBoardChanged)
    grid_layout.addWidget(self.comboBox_bd, rowIdx, 1)

    #&===============================================
    rowIdx += 1

    ACQStartStopPV = PV()
    ACQStartStopPV.SetFullPV("Online_CS_StartStop", False, False, ["Stop", "Start"])

    ACQSaveDataPV = PV()
    ACQSaveDataPV.SetFullPV("Online_CS_SaveData", False, False, ["No Save", "Save"])

    self.ACQStartStop = RTwoStateButton(ACQStartStopPV, parent=self)
    grid_layout.addWidget(self.ACQStartStop, rowIdx, 0)
    self.ACQStartStop.stateChanged.connect(self.OnACQStartStopChanged)

    self.btn_Master = QPushButton("Master Trigger Board")
    self.btn_Master.clicked.connect(self.OpenMasterTriggerWindow)
    grid_layout.addWidget(self.btn_Master, rowIdx, 1)

    rowIdx += 1

    self.ACQSaveData = RTwoStateButton(ACQSaveDataPV, parent=self)
    grid_layout.addWidget(self.ACQSaveData, rowIdx, 0)

    self.combo_Rtr = QComboBox()
    self.combo_Rtr.addItem("Select RTR Board")
    self.combo_Rtr.addItems(RTR_BOARD_LIST)
    self.combo_Rtr.setCurrentIndex(0)
    self.combo_Rtr.currentIndexChanged.connect(lambda index : self.OpenRTRWindow(index))
    grid_layout.addWidget(self.combo_Rtr, rowIdx, 1)

    rowIdx += 1
    self.combo_Dig = QComboBox()
    self.combo_Dig.addItem("Select DIG Board")
    self.combo_Dig.addItems(DIG_BOARD_LIST)
    self.combo_Dig.setCurrentIndex(0)
    self.combo_Dig.currentIndexChanged.connect(lambda index : self.OpenDIGWindow(index))
    grid_layout.addWidget(self.combo_Dig, rowIdx, 1)  

    #=============================== end of GUI setup

    self.totalNumBoards = len(DIG_BOARD_LIST) + len(RTR_BOARD_LIST) + len(MTRG_BOARD_LIST)
    self.generic_board_windows = [None for _ in range(self.totalNumBoards)] 


    self.mtrg_windows = None
    self.rtr_window = [None for _ in range(len(RTR_BOARD_LIST))]
    self.dig_windows = [None for _ in range(len(DIG_BOARD_LIST))]

    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second
  
  def OnACQStartStopChanged(self, state):
    if self.isACQRunning != state:
      self.isACQRunning = state
      print(f"ACQStartStop changed to {state}")

      for dig_win in self.dig_windows:
        if dig_win is not None:
          dig_win.isACQRunning = state

  #&###################################################################
  def closeEvent(self, event):
    print("MainWindow is closing...")

    for gen_win in self.generic_board_windows:
      if gen_win is not None:
        gen_win.close()

    if self.mtrg_windows is not None:
      self.mtrg_windows.close()

    for rtr_win in self.rtr_window:
      if rtr_win is not None:
        rtr_win.close()

    for dig_win in self.dig_windows:
      if dig_win is not None:
        dig_win.close()

    event.accept()


  def UpdatePVs(self):
    self.ACQStartStop.UpdatePV()
    self.ACQSaveData.UpdatePV()


  def OnGenericBoardChanged(self, index):
    if index == 0:
      return
    
    bd_name = self.comboBox_bd.currentText()
    self.comboBox_bd.setCurrentIndex(0)    
    print(f"Board changed to {index}: {bd_name}")

    id = index - 1
    
    if self.generic_board_windows[id] is not None:
      self.generic_board_windows[id].show()
      self.generic_board_windows[id].raise_()
      self.generic_board_windows[id].activateWindow()
      self.generic_board_windows[id].timer.start()  # Restart the timer
      return

    self.generic_board_windows[id] = BoardPVWindow(bd_name, ALLBOARD[id], -1, self)
    self.generic_board_windows[id].show()


  def OpenMasterTriggerWindow(self):
    if self.mtrg_windows is not None:
      self.mtrg_windows.show()
      self.mtrg_windows.raise_()
      self.mtrg_windows.activateWindow()
      return

    self.mtrg_windows = MTRGWindow(MTRG_BOARD_LIST[0], MTRG1)
    self.mtrg_windows.show()

  def OpenRTRWindow(self, index):
    if index == 0:
      return

    id = index - 1
    self.combo_Rtr.setCurrentIndex(0)

    if self.rtr_window[id] is not None:
      self.rtr_window[id].show()
      self.rtr_window[id].raise_()
      self.rtr_window[id].activateWindow()
      return

    self.rtr_window[id] = RTRWindow(RTR_BOARD_LIST[id], RTR_List[id])
    self.rtr_window[id].show()

  def OpenDIGWindow(self, index):
    if index == 0:
      return  
    
    id = index - 1
    self.combo_Dig.setCurrentIndex(0)    

    if self.dig_windows[id] is not None:
      self.dig_windows[id].show()
      self.dig_windows[id].raise_()
      self.dig_windows[id].activateWindow()
      return

    self.dig_windows[id] = DIGWindow(DIG_BOARD_LIST[id], DIG_List[id])
    self.dig_windows[id].show()


##############################################################################
if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())