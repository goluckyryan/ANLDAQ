#!/usr/bin/env python3

import sys
import time

from json2pv import GeneratePVLists

DIG_CHANNEL_PV, DIG_BOARD_PV, RTR_BOARD_PV, MTRG_BOARD_PV, DIG_BOARD_LIST, RTR_BOARD_LIST, MTRG_BOARD_LIST, DAQ_PV, DAQ_LIST = GeneratePVLists('../ioc/All_PV.json')

# exit()

for i, bd in enumerate(DIG_BOARD_LIST):
  print(f"DIG  Board {i:>2d}: {bd}")

for i, bd in enumerate(RTR_BOARD_LIST):
  print(f"RTR  Board {i:>2d}: {bd}")

for i, bd in enumerate(MTRG_BOARD_LIST):
  print(f"MTRG Board {i:>2d}: {bd}")

for i, bd in enumerate(DAQ_LIST):
  print(f"       DAQ {i:>2d}: {bd}")

print("##########################################################################")

from class_Board import Board

DIG_List = []
RTR_List = []

for bd_name in DIG_BOARD_LIST:
  bd = Board()
  bd.SetBoardName(bd_name)
  bd.SetCH_PV(10, DIG_CHANNEL_PV)
  bd.SetBoard_PV(DIG_BOARD_PV)
  DIG_List.append(bd)

for bd_name in RTR_BOARD_LIST:
  bd = Board()
  bd.SetBoardName(bd_name)
  bd.SetBoard_PV(RTR_BOARD_PV)
  RTR_List.append(bd)

MTRG = Board()
MTRG.SetBoardName(MTRG_BOARD_LIST[0])
MTRG.SetBoard_PV(MTRG_BOARD_PV)

DAQ_List = []

for bd_name in DAQ_LIST:
  bd = Board()
  bd.SetBoardName(bd_name)
  bd.SetBoard_PV(DAQ_PV, isDAQ=True)
  DAQ_List.append(bd)

ALLBOARD = DIG_List + RTR_List + [MTRG] + DAQ_List

############################# A GUI window
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QTabWidget, QComboBox, QPushButton, QGroupBox
from custom_QClasses import GLabel, GLineEdit, GFlagDisplay, GTwoStateButton
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel

from class_PVWidgets import RTwoStateButton
from class_PV import PV

from gui_Board import BoardPVWindow
from gui_MTRG import MTRGWindow
from gui_RTR import RTRWindow
from gui_DIG import DIGWindow
from gui_SYS import sysTimestampReadOutTab, sysLinktab, globalSettingTab

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

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #&=============================================== GUI setup
    rowIdx = 0

    #@=========== GroupBox for Start/Stop and Save
    acq_groupbox = QGroupBox("Acquisition Controls")
    acq_layout = QGridLayout()
    acq_groupbox.setLayout(acq_layout)

    ACQStartStopPV = PV()
    ACQStartStopPV.SetFullPV("Online_CS_StartStop", False, False, ["Stop", "Start"])

    ACQSaveDataPV = PV()
    ACQSaveDataPV.SetFullPV("Online_CS_SaveData", False, False, ["No Save", "Save"])

    self.ACQStartStop = RTwoStateButton(ACQStartStopPV, parent=self)
    acq_layout.addWidget(self.ACQStartStop, 0, 0)
    self.ACQStartStop.stateChanged.connect(self.OnACQStartStopChanged)

    self.ACQSaveData = RTwoStateButton(ACQSaveDataPV, parent=self)
    acq_layout.addWidget(self.ACQSaveData, 1, 0)

    layout.addWidget(acq_groupbox, rowIdx, 0, 1, 1)  

    #@=========== GroupBox for Board Selection
    board_groupbox = QGroupBox("Board Selection")
    board_layout = QGridLayout()
    board_groupbox.setLayout(board_layout)

    self.btn_Master = QPushButton("Master Trigger Board")
    self.btn_Master.clicked.connect(self.OpenMasterTriggerWindow)
    board_layout.addWidget(self.btn_Master, 0, 0)

    self.combo_Rtr = QComboBox()
    self.combo_Rtr.addItem("Select RTR Board")
    self.combo_Rtr.addItems(RTR_BOARD_LIST)
    self.combo_Rtr.setCurrentIndex(0)
    self.combo_Rtr.currentIndexChanged.connect(lambda index : self.OpenRTRWindow(index))
    board_layout.addWidget(self.combo_Rtr, 1, 0)

    self.combo_Dig = QComboBox()
    self.combo_Dig.addItem("Select DIG Board")
    self.combo_Dig.addItems(DIG_BOARD_LIST)
    self.combo_Dig.setCurrentIndex(0)
    self.combo_Dig.currentIndexChanged.connect(lambda index : self.OpenDIGWindow(index))
    board_layout.addWidget(self.combo_Dig, 2, 0)

    rowIdx = 0
    layout.addWidget(board_groupbox, rowIdx, 1, 2, 1)  # Span 3 rows

    #@================== Other GroupBox
    other_groupbox = QGroupBox("Others")
    other_layout = QGridLayout()
    other_groupbox.setLayout(other_layout)

    self.script_combo = QComboBox()
    self.script_combo.addItem("Select Script")
    self.script_combo.addItem("Link system")
    self.script_combo.addItem("Reset all boards")

    self.script_combo.setCurrentIndex(0)
    self.script_combo.currentIndexChanged.connect(self.OnScriptChanged)
    other_layout.addWidget(self.script_combo, 0, 0)

    self.terminal_combo = QComboBox()
    self.terminal_combo.addItem("Open Terminal")
    self.terminal_combo.addItem("Soft IOC")
    for i in range(len(DAQ_LIST)):
      self.terminal_combo.addItem(f"IOC-{i}")
    self.terminal_combo.setCurrentIndex(0)
    self.terminal_combo.currentIndexChanged.connect(self.OnOpenTerminal)
    other_layout.addWidget(self.terminal_combo, 1, 0)

    rowIdx = 0
    layout.addWidget(other_groupbox, rowIdx, 2, 2, 1)

    #@================== timestamp tab
    rowIdx += 3
    self.tabWidget = QTabWidget()
    layout.addWidget(self.tabWidget, rowIdx, 0, 1, 3)

    self.timestampTab = sysTimestampReadOutTab(MTRG, RTR_List, DIG_List, DAQ_List)
    self.linkTab = sysLinktab(MTRG, RTR_List)
    self.globalSettingTab = globalSettingTab(MTRG, RTR_List, DIG_List)

    self.tabWidget.addTab(self.timestampTab, "Timestamp/ReadOut")
    self.tabWidget.addTab(self.linkTab, "Link Status")
    self.tabWidget.addTab(self.globalSettingTab, "Global Settings")

    self.tabWidget.currentChanged.connect(lambda _: self.tabWidget.currentWidget().UpdatePVs(True))

    #@=========== Generic Board Selection
    rowIdx += 1
    layout.addWidget(GLabel("Generic Board:"), rowIdx, 0)
    self.comboBox_bd = QComboBox()
    self.comboBox_bd.addItem("Select Board")
    self.comboBox_bd.addItems(DIG_BOARD_LIST)
    self.comboBox_bd.addItems(RTR_BOARD_LIST)
    self.comboBox_bd.addItems(MTRG_BOARD_LIST)
    self.comboBox_bd.addItems(DAQ_LIST)
    self.comboBox_bd.setCurrentIndex(0)
    self.comboBox_bd.currentIndexChanged.connect(self.OnGenericBoardChanged)
    layout.addWidget(self.comboBox_bd, rowIdx, 1)

    #&=============================== end of GUI setup
    self.totalNumBoards = len(ALLBOARD)
    self.generic_board_windows = [None for _ in range(self.totalNumBoards)] 

    self.mtrg_window = None
    self.rtr_windows = [None for _ in range(len(RTR_BOARD_LIST))]
    self.dig_windows = [None for _ in range(len(DIG_BOARD_LIST))]

    self.sys_window = None

    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second

  
  
  #&###################################################################
  def OnACQStartStopChanged(self, state):
    if self.isACQRunning != state:
      self.isACQRunning = state
      print(f"ACQStartStop changed to {state}")

      for dig_win in self.dig_windows:
        if dig_win is not None:
          dig_win.isACQRunning = state

  def closeEvent(self, event):
    print("MainWindow is closing...")

    for gen_win in self.generic_board_windows:
      if gen_win is not None:
        gen_win.close()

    if self.mtrg_window is not None:
      self.mtrg_window.close()

    for rtr_win in self.rtr_windows:
      if rtr_win is not None:
        rtr_win.close()

    for dig_win in self.dig_windows:
      if dig_win is not None:
        dig_win.close()

    if self.sys_window is not None:
      self.sys_window.close()

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
    if self.mtrg_window is not None:
      self.mtrg_window.show()
      self.mtrg_window.raise_()
      self.mtrg_window.activateWindow()
      return

    self.mtrg_window = MTRGWindow(MTRG_BOARD_LIST[0], MTRG)
    self.mtrg_window.show()

  def OpenRTRWindow(self, index):
    if index == 0:
      return

    id = index - 1
    self.combo_Rtr.setCurrentIndex(0)

    if self.rtr_windows[id] is not None:
      self.rtr_windows[id].show()
      self.rtr_windows[id].raise_()
      self.rtr_windows[id].activateWindow()
      return

    self.rtr_windows[id] = RTRWindow(RTR_BOARD_LIST[id], RTR_List[id])
    self.rtr_windows[id].show()

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

  def OnScriptChanged(self, index):
    if index == 0:
      return
    
    script_name = self.script_combo.currentText()
    self.script_combo.setCurrentIndex(0)    

    if script_name == "Link system":
      pass
    elif script_name == "Reset all boards":
      pass

  def OnOpenTerminal(self, index):
    if index == 0:
      return
    
    term_name = self.terminal_combo.currentText()
    self.terminal_combo.setCurrentIndex(0)    
    print(f"Open terminal: {term_name}")

    if term_name == "Soft IOC":
      import os
      #TODO
      os.system("gnome-terminal -- bash -c 'cd ../scripts; ./terminal S; exec bash'")
      return

    if term_name.startswith("IOC-"):
      id = int(term_name.split("-")[-1])
      if id < 0 or id >= len(DAQ_LIST):
        print(f"Invalid DAQ id: {id}")
        return
      
      import os
      os.system(f"gnome-terminal -- bash -c 'cd ../scripts; ./terminal {id}; exec bash'")
      return

##############################################################################
if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())