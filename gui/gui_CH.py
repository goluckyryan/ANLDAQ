from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget, QGroupBox, QPushButton, QFrame, QComboBox, QLabel
from PyQt6.QtCore import Qt, QTimer

from class_Board import Board
from class_PV import PV
from custom_QClasses import GLabel, GLineEdit
from class_PVWidgets import RLineEdit, RTwoStateButton, RComboBox
from gui_RAM import RAMWindow
import re

from aux import make_pattern_list, natural_key

from gui_MTRG import templateTab


#^###########################################################################################################
class CHWindow(QMainWindow):
  def __init__(self, board_name, ch,  board : Board):
    super().__init__()

    self.ch = ch
    self.board = board

    self.setWindowTitle(board_name)
    self.setGeometry(150, 150, 600, 600)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #================================ PV Widgets
    self.pvWidgetList = []

    #&================================ General Settings
    general_pvNameList = [
      ["channel_enable",         "Enable",           False, "twoState"],
      ["trigger_polarity",       "Polarity",         False, "twoState"],
      ["pileup_mode",            "Pileup",           False, "twoState"],
      ["cfd_esum_mode",          "CFD E-Sum Mode",   False, "twoState"],
      ["CFD_fraction",           "CFD Frac.",        False, "lineEdit"],
      ["reg_channel_control",    "Control reg",      False, "lineEdit"],
      ["preamp_reset_delay_en",  "Preamp Reset En.", False, "twoState"],   
      ["preamp_reset_delay",     "Preamp Reset",     False, "lineEdit"]
    ]

    general_group = QGroupBox("General Settings")
    general_layout = QGridLayout()
    general_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignLeft)
    general_group.setLayout(general_layout)

    self.FillWidgets(general_layout, general_pvNameList, maxRows=9, widgetWidth=100)

    #&================================ Window Settings
    window_pvNameList = [
      ["led_threshold",  "Threshold",    False, "lineEdit"],
      ["k0_window",      "k0",           False, "lineEdit"],
      ["k_window",       "k",            False, "lineEdit"],
      ["d_window",       "d",            False, "lineEdit"],
      ["d3_window",      "d3",           False, "lineEdit"],
      ["m_window",       "m",            False, "lineEdit"],
      ["p1_window",      "p1",           False, "lineEdit"],
      ["p2_window",      "p2",           False, "lineEdit"],
      ["raw_data_delay", "Trace Delay",  False, "lineEdit"],
      ["raw_data_length","Trace Length", False, "lineEdit"]
    ]

    window_group = QGroupBox("Window Settings")
    window_layout = QGridLayout()
    window_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignLeft)
    window_group.setLayout(window_layout)

    self.FillWidgets(window_layout, window_pvNameList, maxRows=10, widgetWidth=100)

    #================================= Layout
    layout.addWidget(general_group, 0, 0, 1, 1)
    layout.addWidget(window_group,  0, 1, 1, 1)

    #================================ QTimer for updating PVs
    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second


  #################################################################
  def FindChannelPV(self,  pv_name) -> PV:
    for pv in self.board.CH_PV[self.ch]:
      pvName = pv.name.split(":")[-1]
      if pvName.startswith(pv_name):
        return pv
    return None
  

  def FillWidgets(self, layout: QGridLayout, pvNameList, maxRows = 9, widgetWidth = 100):
    row = 0
    col = 0

    for pvName, displayName, isHex, type in pvNameList:
      pv = self.FindChannelPV(pvName)
      if pv is not None:
        layout.addWidget(GLabel(displayName, alignment=Qt.AlignmentFlag.AlignRight), row, col)

        if type == "lineEdit":
          if isHex:
            pvWidget = RLineEdit(pv, hexBinDec="hex", width= widgetWidth, parent=self)
          else: 
            pvWidget = RLineEdit(pv, width= widgetWidth, parent=self)
        elif type == "twoState":
          pvWidget = RTwoStateButton(pv, width= widgetWidth, parent=self)
        elif type == "comboBox":
          pvWidget = RComboBox(pv, width= widgetWidth, parent=self)
        layout.addWidget(pvWidget, row, col + 1)
        self.pvWidgetList.append(pvWidget)
        row += 1
        if row >= maxRows:
          row = 0
          col += 2

  def UpdatePVs(self):
    if not self.isVisible():
      return

    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV()

