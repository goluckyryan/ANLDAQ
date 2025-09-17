#!/usr/bin/env python3

import sys
import time

############################# load the json file to contains all PVs
import json

# Open and read the JSON file
with open('../ioc/All_PV.json', 'r', encoding='utf-8') as f:
  data = json.load(f)


DIG_BOARD_PV = []
DIG_CHANNEL_PV = []

MTRG_BOARD_PV = []
RTRG_BOARD_PV = []

count = 0
for item in data:
  if "MDIG" in item[0]:

    if "led_green_state" in item[0]:
      pvFirst = item[0].split(":")[:-1]
      PV = pvFirst[0]+ ":" + pvFirst[1] + ":led_green_state"
      if PV not in DIG_CHANNEL_PV:
        DIG_CHANNEL_PV.append(PV)
    elif "led_red_state" in item[0]:
      pvFirst = item[0].split(":")[:-1]
      PV = pvFirst[0]+ ":" + pvFirst[1] + ":led_red_state"
      if PV not in DIG_CHANNEL_PV:
        DIG_CHANNEL_PV.append(PV)

    elif item[0][-1].isdigit():
      PV = item[0][:-1]
      if PV not in DIG_CHANNEL_PV:
        DIG_CHANNEL_PV.append(PV)
      else:
        pass

    elif item[0].endswith("RBV"):
      PV = item[0][:-4]
      if PV[-1].isdigit():
        if PV[:-1] not in DIG_CHANNEL_PV:
          DIG_CHANNEL_PV.append(PV[:-1])
        else:
          pass
      else:
        if PV not in DIG_BOARD_PV:
          DIG_BOARD_PV.append(PV)
        else:
          pass

    elif item[0].endswith("LONGOUT") or item[0].endswith("LONGIN"):
      PV = item[0][:-7]
      if PV[-1].isdigit():
        if PV[:-1] not in DIG_CHANNEL_PV:
          DIG_CHANNEL_PV.append(PV[:-1])
        else:
          pass

    else:
      DIG_BOARD_PV.append(item[0])

  elif "MTRG" in item[0]:
    MTRG_BOARD_PV.append(item[0])

  elif "RTR" in item[0]:
    RTRG_BOARD_PV.append(item[0])

    #print(json.dumps(item, separators=(',', ': '), ensure_ascii=False))


# print(f"Total {len(DIG_BOARD_PV)} digitizer boards, {len(DIG_CHANNEL_PV)} digitizer channels")
# print(f"Total {len(MTRG_BOARD_PV)} master trigger boards")
# print(f"Total {len(RTRG_BOARD_PV)} remote trigger boards")


# for i,  pv in enumerate(DIG_BOARD_PV):
#   print(f"{i:03d} | {pv}")

# for i,  pv in enumerate(DIG_CHANNEL_PV):
#   print(f"{i:03d} | {pv}")


############################# PYEPICS
import epics
epics.ca.initialize_libca()
print(f"PyEpics using libca: {epics.ca.find_libca()}")

############################# A GUI window
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QSpinBox

from custom_QClasses import GLabel, GLineEdit, GFlagDisplay


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Commander")
    self.setGeometry(100, 100, 600, 200)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    grid_layout = QGridLayout()
    central_widget.setLayout(grid_layout)

    rowIndex = 0
    grid_layout.addWidget(GLabel("CH:"), rowIndex, 0)
    self.spinBox_ch = QSpinBox()
    self.spinBox_ch.setRange(0, 9)
    self.spinBox_ch.setValue(0)
    self.spinBox_ch.valueChanged.connect(self.GetAllPV)
    grid_layout.addWidget(self.spinBox_ch, rowIndex, 1)

    rowIndex += 1
    btn_refresh = QPushButton("Refresh")
    btn_refresh.clicked.connect(self.GetAllPV)
    grid_layout.addWidget(btn_refresh, rowIndex, 0, 1, 2)

    self.ch_lineEdit = []

    for i, pv in enumerate(DIG_CHANNEL_PV):
      pvName = pv.split(":")[-1]
      if pvName.startswith("reg_"):
        continue
      rowIndex += 1
      grid_layout.addWidget(GLabel(f"{pvName}"), rowIndex, 0)
      lineEdit = GLineEdit("")
      lineEdit.setToolTip(pv)
      lineEdit.returnPressed.connect(lambda pv=pv, le=lineEdit: self.SetPV(pv, le))
      self.ch_lineEdit.append(lineEdit)
      grid_layout.addWidget(lineEdit, rowIndex, 1)

        
      grid_layout.setColumnStretch(0, 0)
      grid_layout.setColumnStretch(1, 1)

    self.GetAllPV()

  #=======================================
  def GetAllPV(self):
    for i, lineEdit in enumerate(self.ch_lineEdit):
      pv = lineEdit.toolTip()
      ch = self.spinBox_ch.value()
      pv_name = f"{pv}{ch}_RBV"
      p = epics.PV(pv_name)
      try:
        value = p.get()
        # print(f"Accessing PV: {pv_name} Value: {value}")
        lineEdit.setText(str(value))
        lineEdit.setStyleSheet("")
      except Exception as e:
        print(f"Error accessing PV {pv_name}: {e}")
        lineEdit.setText("Err")

   

  def SetPV(self, pv, lineEdit):
    ch = self.spinBox_ch.value()
    pv_name = f"{pv}{ch}"
    value = lineEdit.text()

    print(f"Setting PV: {pv_name} to {value}")

    p = epics.PV(pv_name)
    p.put(value)

    time.sleep(2.0)

    rbv_name = f"{pv_name}_RBV"
    rbv = epics.PV(rbv_name)
    rbv_value = rbv.get()
    lineEdit.setText(str(rbv_value))
    if float(rbv_value) != float(value):
      lineEdit.setStyleSheet("background-color: red;")
    else:
      lineEdit.setStyleSheet("")












if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())