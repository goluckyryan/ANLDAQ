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

# ############################# PYEPICS
# import epics
# epics.ca.initialize_libca()
# print(f"PyEpics using libca: {epics.ca.find_libca()}")

############################# A GUI window
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QSpinBox, QComboBox
from custom_QClasses import GLabel, GLineEdit, GFlagDisplay, GTwoStateButton
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel

from gui_Board import BoardPVWindow


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Commander")
    self.setGeometry(100, 100, 400, 200)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    grid_layout = QGridLayout()
    central_widget.setLayout(grid_layout)

    #=============================== GUI setup
    rowIdx = 0

    grid_layout.addWidget(GLabel("Digitizer Board:"), rowIdx, 0)
    self.comboBox_bd = QComboBox()
    self.comboBox_bd.addItem("Select Board")
    self.comboBox_bd.addItems(DIG_BOARD_LIST)
    self.comboBox_bd.setCurrentIndex(0)
    self.comboBox_bd.currentIndexChanged.connect(self.OnBoardChanged)
    grid_layout.addWidget(self.comboBox_bd, rowIdx, 1)


    rowIdx += 1
    grid_layout.addWidget(GLabel("RTR Board:"), rowIdx, 0)
    self.comboBox_rtr = QComboBox()
    self.comboBox_rtr.addItem("Select Board")
    self.comboBox_rtr.addItems(RTR_BOARD_LIST)
    self.comboBox_rtr.setCurrentIndex(0)
    self.comboBox_rtr.currentIndexChanged.connect(self.OnBoardChanged_rtr)
    grid_layout.addWidget(self.comboBox_rtr, rowIdx, 1)


    # rowIdx += 1
    # grid_layout.addWidget(GLabel("MTRG Board:"), rowIdx, 0)
    # self.comboBox_mtrg = QComboBox()
    # self.comboBox_mtrg.addItem("Select Board")
    # self.comboBox_mtrg.addItems(MTRG_BOARD_LIST)
    # self.comboBox_mtrg.setCurrentIndex(0)
    # self.comboBox_mtrg.currentIndexChanged.connect(self.OnBoardChanged_mtrg)
    # grid_layout.addWidget(self.comboBox_mtrg, rowIdx, 1)

    #=============================== end of GUI setup

    self.board_windows = None
    self.rtr_windows = None
    self.mtrg_windows = None

  ############################################################################
  def closeEvent(self, event):
    print("MainWindow is closing...")
    if self.board_windows is not None:
      print("Closing board window")
      self.board_windows.close()
    if self.rtr_windows is not None:
      print("Closing rtr window")
      self.rtr_windows.close()
    if self.mtrg_windows is not None:
      self.mtrg_windows.close()
    event.accept()


  def OnBoardChanged(self, index):
    if index == 0:
      return
    
    bd_name = self.comboBox_bd.currentText()
    self.comboBox_bd.setCurrentIndex(0)    
    print(f"Board changed to {index}: {bd_name}")

    if self.board_windows is not None:
      self.board_windows.show()
      self.board_windows.raise_()
      self.board_windows.activateWindow()
      self.board_windows.timer.start()  # Restart the timer
      return

    self.board_windows = BoardPVWindow(bd_name, DIG1, -1, self)
    self.board_windows.show()

  def OnBoardChanged_rtr(self, index):
    if index == 0:
      return
    
    bd_name = self.comboBox_rtr.currentText()
    self.comboBox_rtr.setCurrentIndex(0)    
    print(f"Board changed to {index}: {bd_name}")

    # Check if the window exists and is visible
    if self.rtr_windows is not None:
      self.rtr_windows.show()
      self.rtr_windows.raise_()
      self.rtr_windows.activateWindow()
      return

    self.rtr_windows = BoardPVWindow(bd_name, RTR1, -1, self)
    self.rtr_windows.show()
    return

  # def OnBoardChanged_mtrg(self, index):
  #   if index == 0:
  #     return
    
  #   bd_name = self.comboBox_mtrg.currentText()
  #   self.comboBox_mtrg.setCurrentIndex(0)    
  #   print(f"Board changed to {index}: {bd_name}")

  #   if self.mtrg_windows is not None:
  #     self.mtrg_windows.raise_()
  #     self.mtrg_windows.activateWindow()
  #     return

  #   self.mtrg_windows = BoardPVWindow(bd_name, MTRG1, -1, self)
  #   self.mtrg_windows.show()


if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())