#!/usr/bin/env python3

import sys
import time

from json2pv import GeneratePVLists

DIG_CHANNEL_PV, DIG_BOARD_PV = GeneratePVLists('../ioc/All_PV.json')

print("##########################################################################")

from class_dig import DIG
DIG1 = DIG()
DIG1.SetBoardID("VME99", "MDIG1")
DIG1.SetCH_PV(DIG_CHANNEL_PV)
DIG1.SetBoard_PV(DIG_BOARD_PV)

# for i, ch_pv in enumerate(DIG1.CH_PV[0]):
#   print(f"PV {i:02d}: {ch_pv.name}")

# for i, bd_pv in enumerate(DIG1.Board_PV):
#   print(f"PV {i:02d}: {bd_pv.name}, {bd_pv.Type}, RBV_exist={bd_pv.RBV_exist}, States={bd_pv.States}")

pv_id = 13
print(f"=================== Reading PV {DIG_CHANNEL_PV[pv_id].name} for all channels:")

for i in range(10):
  DIG1.CH_PV[i][pv_id].GetValue(fromEPICS=True)
  print(f"Channel {i}: {DIG1.CH_PV[i][pv_id].value} = {DIG1.CH_PV[i][pv_id].char_value}")


print("##########################################################################")
for i , pv in enumerate(DIG1.Board_PV):
  pv.GetValue(fromEPICS=True)
  print(f"PV {i:02d}: {pv.name}, {pv.value} = {pv.char_value} | {pv.RBV_exist}")


exit()


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

    time.sleep(1.0)

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