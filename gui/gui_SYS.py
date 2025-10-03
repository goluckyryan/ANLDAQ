from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget, QGroupBox, QPushButton, QFrame, QComboBox, QLabel
from PyQt6.QtCore import Qt, QTimer

from class_Board import Board
from class_PV import PV
from custom_QClasses import GLabel, GLineEdit
from class_PVWidgets import RLineEdit, RTwoStateButton, RComboBox

#^###########################################################################################################
class sysTemplateTab(QWidget):
  def __init__(self, MTRG : Board, RTR_list, DIG_list, parent=None):
    super().__init__(parent)

    self.MTRG = MTRG
    self.RTR_list = RTR_list
    self.DIG_list = DIG_list

    self.pvWidgetList = []
  
    #------------------------------ QTimer for updating PVs
    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second

  def FindPV(self, pv_name, board : Board) -> PV:
    for pv in board.Board_PV:
      pvName = pv.name.split(":")[-1]
      if pvName == pv_name:
        return pv
    return None

  def UpdatePVs(self, forced = False):
    if not self.isVisible():
      return None
    for pvWidget in self.pvWidgetList:

      pvName = pvWidget.pv.name.split(":")[-1]
      if pvName.startswith("reg_TIMESTAMP_"):
        forced = True

      pvWidget.UpdatePV(forced)

#@===================================================================================
class timestampTab(sysTemplateTab):
  def __init__(self, MTRG : Board, RTR_list, DIG_list, parent=None):
    super().__init__(MTRG, RTR_list, DIG_list, parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    row = 0

    #&================ MTRG Timestamp
    layout.addWidget(GLabel("MTRG :"), row, 0)

    le_mtrg_timeA = RLineEdit(self.FindPV("reg_TIMESTAMP_A",self.MTRG),  hexBinDec = "hex")
    le_mtrg_timeB = RLineEdit(self.FindPV("reg_TIMESTAMP_B",self.MTRG),  hexBinDec = "hex")
    le_mtrg_timeC = RLineEdit(self.FindPV("reg_TIMESTAMP_C",self.MTRG),  hexBinDec = "hex")

    self.pvWidgetList.append(le_mtrg_timeA)
    self.pvWidgetList.append(le_mtrg_timeB)
    self.pvWidgetList.append(le_mtrg_timeC)

    layout.addWidget(le_mtrg_timeA, row, 1)
    layout.addWidget(le_mtrg_timeB, row, 2)
    layout.addWidget(le_mtrg_timeC, row, 3)

    #&================ RTR Timestamp
    row += 1

    for i, rtr in enumerate(self.RTR_list):
      layout.addWidget( GLabel(f"RTR-{i}"), row, 0)

      le_rtr_timeA = RLineEdit(self.FindPV("reg_TIMESTAMP_A", rtr), hexBinDec = "hex")
      le_rtr_timeB = RLineEdit(self.FindPV("reg_TIMESTAMP_B", rtr), hexBinDec = "hex")
      le_rtr_timeC = RLineEdit(self.FindPV("reg_TIMESTAMP_C", rtr), hexBinDec = "hex")

      self.pvWidgetList.append(le_rtr_timeA)
      self.pvWidgetList.append(le_rtr_timeB)
      self.pvWidgetList.append(le_rtr_timeC)

      layout.addWidget(le_rtr_timeA, row, 1)
      layout.addWidget(le_rtr_timeB, row, 2)
      layout.addWidget(le_rtr_timeC, row, 3)
      row += 1

    #&================ DIG Timestamp



#^###########################################################################################################
class SYSWindow(QMainWindow):
  def __init__(self, MTRG : Board, RTR_list, DIG_list):
    super().__init__()

    self.setWindowFlags(
      Qt.WindowType.Window |
      Qt.WindowType.WindowMinimizeButtonHint |
      Qt.WindowType.WindowCloseButtonHint
    )

    self.MTRG = MTRG
    self.RTR_list = RTR_list
    self.DIG_list = DIG_list

    self.isACQRunning = False

    self.setWindowTitle("System Overview")
    self.setGeometry(150, 150, 1000, 600)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #================================ PV Widgets
    self.pvWidgetList = []


    #&================================== GUI

    #@================== timestamp tab
    self.tabWidget = QTabWidget()
    layout.addWidget(self.tabWidget, 0, 0)

    self.timestampTab = timestampTab(self.MTRG, self.RTR_list, self.DIG_list)
    self.tabWidget.addTab(self.timestampTab, "Timestamp")


    #================================ QTimer for updating PVs
    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second

  #################################################################

  def FindPV(self,  pv_name, board : Board) -> PV:
    for pv in board.Board_PV:
      pvName = pv.name.split(":")[-1]
      if pvName == pv_name:
        return pv
    return None
  
  def FindChannelPV(self, channel : int, pv_name, board : Board) -> PV:
    for pv in board.CH_PV[channel]:
      pvName = pv.name.split(":")[-1]
      if pvName.startswith(pv_name):
        return pv
    return None
  
  def UpdatePVs(self):
    if not self.isVisible():
      return
    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV()
