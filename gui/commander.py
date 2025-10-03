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
DIG1 = Board()
DIG1.SetBoardID(DIG_BOARD_LIST[0])
DIG1.SetCH_PV(10, DIG_CHANNEL_PV)
DIG1.SetBoard_PV(DIG_BOARD_PV)

RTR1 = Board()
RTR1.SetBoardID(RTR_BOARD_LIST[0])
RTR1.SetBoard_PV(RTR_BOARD_PV)

MTRG1 = Board()
MTRG1.SetBoardID(MTRG_BOARD_LIST[0])
MTRG1.SetBoard_PV(MTRG_BOARD_PV)

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

    self.btn_Rtr = QPushButton("RTR Board")
    self.btn_Rtr.clicked.connect(self.OpenRTRWindow)
    grid_layout.addWidget(self.btn_Rtr, rowIdx, 1)

    rowIdx += 1
    self.btn_Dig = QPushButton("DIG Board")
    self.btn_Dig.clicked.connect(self.OpenDIGWindow)
    grid_layout.addWidget(self.btn_Dig, rowIdx, 1)  

    #=============================== end of GUI setup

    self.generic_board_windows = None
    self.generic_rtr_windows = None
    self.generic_mtrg_windows = None

    self.mtrg_windows = None
    self.rtr_window = None
    self.dig_windows = None

    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second
  
  def OnACQStartStopChanged(self, state):
    if self.isACQRunning != state:
      self.isACQRunning = state
      print(f"ACQStartStop changed to {state}")

      if self.dig_windows is not None:
        self.dig_windows.isACQRunning = state

  #^###################################################################
  #^###################################################################
  #^###################################################################
  def closeEvent(self, event):
    print("MainWindow is closing...")
    if self.generic_board_windows is not None:
      self.generic_board_windows.close()

    if self.generic_rtr_windows is not None:
      self.generic_rtr_windows.close()

    if self.generic_mtrg_windows is not None:
      self.generic_mtrg_windows.close()

    if self.mtrg_windows is not None:
      self.mtrg_windows.close()

    if self.rtr_window is not None:
      self.rtr_window.close()

    if self.dig_windows is not None:
      self.dig_windows.close()

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

    
    if bd_name in DIG_BOARD_LIST:    
      if self.generic_board_windows is not None:
        self.generic_board_windows.show()
        self.generic_board_windows.raise_()
        self.generic_board_windows.activateWindow()
        self.generic_board_windows.timer.start()  # Restart the timer
        return

      self.generic_board_windows = BoardPVWindow(bd_name, DIG1, -1, self)
      self.generic_board_windows.show()

    elif bd_name in MTRG_BOARD_LIST:
      if self.generic_mtrg_windows is not None:
        self.generic_mtrg_windows.show()
        self.generic_mtrg_windows.raise_()
        self.generic_mtrg_windows.activateWindow()
        return

      self.generic_mtrg_windows = BoardPVWindow(bd_name, MTRG1, -1, self)
      self.generic_mtrg_windows.show()

    elif bd_name in RTR_BOARD_LIST:
      if self.generic_rtr_windows is not None:
        self.generic_rtr_windows.show()
        self.generic_rtr_windows.raise_()
        self.generic_rtr_windows.activateWindow()
        return

      self.generic_rtr_windows = BoardPVWindow(bd_name, RTR1, -1, self)
      self.generic_rtr_windows.show()


  def OpenMasterTriggerWindow(self):
    if self.mtrg_windows is not None:
      self.mtrg_windows.show()
      self.mtrg_windows.raise_()
      self.mtrg_windows.activateWindow()
      return

    self.mtrg_windows = MTRGWindow(MTRG_BOARD_LIST[0], MTRG1)
    self.mtrg_windows.show()

  def OpenRTRWindow(self):
    if self.rtr_window is not None:
      self.rtr_window.show()
      self.rtr_window.raise_()
      self.rtr_window.activateWindow()
      return

    self.rtr_window = RTRWindow(RTR_BOARD_LIST[0], RTR1)
    self.rtr_window.show()

  def OpenDIGWindow(self):
    if self.dig_windows is not None:
      self.dig_windows.show()
      self.dig_windows.raise_()
      self.dig_windows.activateWindow()
      return

    self.dig_windows = DIGWindow(DIG_BOARD_LIST[0], DIG1)
    self.dig_windows.show()


##############################################################################
if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())