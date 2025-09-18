#!/usr/bin/env python3

import sys
import time

############################# load the json file to contains all PVs
import json

# Open and read the JSON file
with open('../ioc/All_PV.json', 'r', encoding='utf-8') as f:
  data = json.load(f)


temp_DIG_BOARD_PV = []
temp_DIG_CHANNEL_PV = []

MTRG_BOARD_PV = []
RTRG_BOARD_PV = []

for item in data:
  if "MDIG" in item[0]:

    subField = item[1]

    isChannel = False
    if "led_green_state" in item[0]:
      pvFirst = item[0].split(":")[:-1]
      pv = pvFirst[0]+ ":" + pvFirst[1] + ":led_green_state"
      subField["RBV"] = "ONLY"
      isChannel = True
    
    elif "led_red_state" in item[0]:
      pvFirst = item[0].split(":")[:-1]
      pv = pvFirst[0]+ ":" + pvFirst[1] + ":led_red_state"
      subField["RBV"] = "ONLY"
      isChannel = True

    elif item[0][-1].isdigit():
      pv = item[0][:-1]
      isChannel = True
    
    elif item[0].endswith("RBV"):
      pv = item[0][:-4]
      if pv[-1].isdigit():
        pv = pv[:-1]
        subField["RBV"] = "ONLY"
        isChannel = True
      else:
        isChannel = False

    elif item[0].endswith("LONGOUT") or item[0].endswith("LONGIN"):
      pv = item[0][:-7]
      if pv[-1].isdigit():
        pv = pv[:-1]
        isChannel = True
    else:
      pv = item[0]
      isChannel = False

    if isChannel:
      if pv not in [x[0] for x in temp_DIG_CHANNEL_PV]:
        pv = (pv, subField) 
        temp_DIG_CHANNEL_PV.append(pv)
    else:
      if pv not in temp_DIG_BOARD_PV:
        temp_DIG_BOARD_PV.append(pv)

  elif "MTRG" in item[0]:
    MTRG_BOARD_PV.append(item[0])

  elif "RTR" in item[0]:
    RTRG_BOARD_PV.append(item[0])


# for i,  pv in enumerate(temp_DIG_CHANNEL_PV):
#   print(f"{i:03d} | {pv[0]:40s} | {pv[1]}")

print("##########################################################################")

#========================== check the pv[1] and reformate if needed
from class_PV import PV

DIG_CHANNEL_PV = []

for i, pv in enumerate(temp_DIG_CHANNEL_PV):

  pvName = pv[0].split(":")[-1]
  if pvName.startswith("reg_") or pvName.startswith("regin_"):
    continue

  PV_obj = PV()
  PV_obj.SetName(pv[0])

  field_names = [x for x in pv[1]]
  field_value = [pv[1][x] for x in pv[1]]

  states = []

  for fn, fv in zip(field_names, field_value):
    if fn == "Type":
      PV_obj.SetType(fv)
    elif fn == "RBV":
      if fv == "ONLY":
        PV_obj.SetReadOnly(True)
      else:
        PV_obj.SetReadOnly(False)
    if fn.endswith("NAM") or fn.endswith("ST"):
      PV_obj.AddState(fv)

  DIG_CHANNEL_PV.append(PV_obj)


for i,  pv in enumerate(DIG_CHANNEL_PV):
  print(f"{i:03d} | {pv}")


############################# PYEPICS
import epics
epics.ca.initialize_libca()
print(f"PyEpics using libca: {epics.ca.find_libca()}")

############################# A GUI window
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QGridLayout, QSpinBox, QComboBox

from custom_QClasses import GLabel, GLineEdit, GFlagDisplay, GTwoStateButton
from PyQt6.QtCore import QThread, QObject, pyqtSignal


class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()
    self.setWindowTitle("Commander")
    self.setGeometry(100, 100, 400, 200)

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

    self.chPVWidgetList = []

    self.StopSignal = True

    for i, pv in enumerate(DIG_CHANNEL_PV):
      pvName = pv.name.split(":")[-1]
      rowIndex += 1
# 
      #if two states, use GTwoStateButton
      if pv.NumStates() == 2:
        grid_layout.addWidget(GLabel(f"{pvName}"), rowIndex, 0)
        btn = GTwoStateButton(pv.States[0], pv.States[1], color="green")
        btn.setToolTip(pv.name)
        if pv.ReadOnly:
          btn.setEnabled(False)
        btn.clicked.connect(lambda checked, pv=pv, btn=btn: self.SetPV(pv, btn))
        self.chPVWidgetList.append(btn)
        grid_layout.addWidget(btn, rowIndex, 1)
        continue

      elif pv.NumStates() > 2: #use QComboBox
        grid_layout.addWidget(GLabel(f"{pvName}"), rowIndex, 0)
        combo = QComboBox()
        combo.setToolTip(pv.name)
        combo.addItems(pv.States)
        combo.currentIndexChanged.connect(lambda index, pv=pv, combo=combo: self.SetPV(pv, combo))
        self.chPVWidgetList.append(combo)
        grid_layout.addWidget(combo, rowIndex, 1)
        continue

      else:
        grid_layout.addWidget(GLabel(f"{pvName}"), rowIndex, 0)
        lineEdit = GLineEdit("")
        lineEdit.setToolTip(pv.name)
        lineEdit.returnPressed.connect(lambda pv=pv, le=lineEdit: self.SetPV(pv, le))
        self.chPVWidgetList.append(lineEdit)
        if pv.ReadOnly:
          lineEdit.setReadOnly(True)
          lineEdit.setStyleSheet("background-color: lightgray;")
        grid_layout.addWidget(lineEdit, rowIndex, 1)

        
      grid_layout.setColumnStretch(0, 0)
      grid_layout.setColumnStretch(1, 1)


    #=============================== end of GUI setup

    self.GetAllPV()

    # create a QThread to GetAllPV for ch 1 to 9

    class Worker(QObject):
      def run(self):
        for ch in range(1, 10):
          self.GetAllPV(ch)
          
    self.thread = QThread()
    self.worker = Worker()
    self.worker.moveToThread(self.thread)
    self.thread.start()

    self.StopSignal = False

  #=======================================
  def GetAllPV(self, ch = None):
    self.StopSignal = True
    for i, pv in enumerate(DIG_CHANNEL_PV):
      if ch is None:
        ch = self.spinBox_ch.value()
      pv_name = f"{pv.name}{ch}_RBV"
      p = epics.PV(pv_name)
      try:
        value = p.get()
        wdg = self.chPVWidgetList[i]
        if isinstance(wdg, GLineEdit):
          wdg.setText(str(value))
          pv.SetValue(value)
          wdg.setStyleSheet("")
        elif isinstance(wdg, GTwoStateButton):
          pv.SetValue(p.char_value)
          if p.char_value == pv.States[0]:
            wdg.setState(False)
          else:
            wdg.setState(True)
          wdg.updateAppearance()
        elif isinstance(wdg, QComboBox):
          pv.SetValue(p.char_value)
          if p.char_value in pv.States:
            index = wdg.findText(str(p.char_value))
            wdg.setCurrentIndex(index)         
      except Exception as e:
        print(f"Error accessing PV {pv_name}: {e}")

      QApplication.processEvents()
    self.StopSignal = False
   
  def SetPV(self, pv, wdg):
    if self.StopSignal:
      return
    ch = self.spinBox_ch.value()
    pv_name = f"{pv.name}{ch}"
    p = epics.PV(pv_name)

    if isinstance(wdg, GTwoStateButton):
      if wdg.state:
        value = pv.States[1]
      else:
        value = pv.States[0]
    elif isinstance(wdg, QComboBox):
      value = wdg.currentText()
    elif isinstance(wdg, GLineEdit):
      value = wdg.text()

    print(f"Setting PV: {pv_name} to {value}")
    p.put(value)

    time.sleep(2.0)

    rbv_name = f"{pv_name}_RBV"
    rbv = epics.PV(rbv_name)
    rbv_value = rbv.get()

    if isinstance(wdg, GLineEdit):
      wdg.setText(str(rbv_value))
      if float(rbv_value) != float(value):
        wdg.setStyleSheet("background-color: red;")
      else:
        pv.SetValue(rbv_value)
        wdg.setStyleSheet("")
    elif isinstance(wdg, GTwoStateButton):
      print(f"RBV value: {rbv.char_value}, Expected value: {value}")
      if rbv.char_value != value:
        wdg.setStyleSheet("background-color: red;")
      else:
        pv.SetValue(rbv.char_value)
        wdg.updateAppearance()
    elif isinstance(wdg, QComboBox):
      print(f"RBV value: {rbv.char_value}, Expected value: {value}")
      if rbv.char_value != value:
        wdg.setStyleSheet("background-color: red;")
      else:
        pv.SetValue(rbv.char_value)
        wdg.setStyleSheet("")











if __name__ == "__main__":
  app = QApplication(sys.argv)
  window = MainWindow()
  window.show()
  sys.exit(app.exec())