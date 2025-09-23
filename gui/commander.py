#!/usr/bin/env python3

import sys
import time

from json2pv import GeneratePVLists

DIG_CHANNEL_PV, DIG_BOARD_PV, RTR_BOARD_PV, MTRG_BOARD_PV, DIG_BOARD_LIST, RTR_BOARD_LIST, MTRG_BOARD_LIST = GeneratePVLists('../ioc/All_PV.json')

for i, bd in enumerate(DIG_BOARD_LIST):
  print(f"DIG  Board {i:>2d}: {bd}")

for i, bd in enumerate(RTR_BOARD_LIST):
  print(f"RTR  Board {i:>2d}: {bd}")

for i, bd in enumerate(MTRG_BOARD_LIST):
  print(f"MTRG Board {i:>2d}: {bd}")

print("##########################################################################")

from class_DIG import DIG
DIG1 = DIG()
DIG1.SetBoardID(DIG_BOARD_LIST[0])
DIG1.SetCH_PV(DIG_CHANNEL_PV)
DIG1.SetBoard_PV(DIG_BOARD_PV)

# ############################# PYEPICS
# import epics
# epics.ca.initialize_libca()
# print(f"PyEpics using libca: {epics.ca.find_libca()}")

############################# A GUI window
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QSpinBox, QComboBox
from custom_QClasses import GLabel, GLineEdit, GFlagDisplay, GTwoStateButton
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel

from class_DIG_GUI import BoardPVWindow


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

    #=============================== end of GUI setup

  def OnBoardChanged(self, index):
    bd_name = self.comboBox_bd.currentText()
    if index == 0:
      return
    print(f"Board changed to {index}: {bd_name}")

    # Show the board PVs in a new window
    pv_window = BoardPVWindow(bd_name, DIG1, self)
    pv_window.show()



if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())