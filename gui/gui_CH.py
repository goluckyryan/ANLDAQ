from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget, QGroupBox, QComboBox, QLabel, QScrollArea
from PyQt6.QtCore import Qt, QTimer

from class_Board import Board
from class_PV import PV
from custom_QClasses import GLabel, GLineEdit
from class_PVWidgets import RLineEdit, RTwoStateButton, RComboBox, RSetButton
from gui_RAM import RAMWindow
import re

from aux import make_pattern_list, natural_key

from gui_MTRG import templateTab

#^###########################################################################################################
class ChTabTamplate(QWidget):
  def __init__(self, board : Board, parent=None):
    super().__init__(parent)
    self.board = board
    self.pvWidgetList = []

    #================================ QTimer for updating PVs
    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second

  def FindPV(self, pv_name) -> PV:
    for pv in self.board.Board_PV:
      pvName = pv.name.split(":")[-1]
      if pvName == pv_name:
        return pv
    return None

  def FindChannelPV(self, ch,  pv_name) -> PV:
    for pv in self.board.CH_PV[ch]:
      pvName = pv.name.split(":")[-1]
      if pvName.startswith(pv_name):
        return pv
    return None

  def UpdatePVs(self, forced = False):
    if not self.isVisible():
      return
    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV(forced)

#/###########################################################
class ChannelTab(ChTabTamplate):
  def __init__(self, board : Board, parent=None):
    super().__init__(board, parent)
    layout = QGridLayout()
    self.setLayout(layout)

    self.ch = 0

    rowIdx = 0
    colIdx = 0

    layout.addWidget(QLabel(f"Channel : "), rowIdx, colIdx)
    self.chSelector = QComboBox(parent=self)
    for i in range(self.board.NumChannels):
      self.chSelector.addItem(f"{i}")
    self.chSelector.currentIndexChanged.connect(self.on_channel_changed)
    layout.addWidget(self.chSelector, rowIdx, colIdx + 1)

    #&================================ General Settings
    general_pvNameList = [
      ["channel_enable",         "Enable",              False],
      ["trigger_polarity",       "Polarity",            False],
      ["pileup_mode",            "Pileup",              False],
      ["cfd_esum_mode",          "CFD E-Sum Mode",      False],
      ["CFD_fraction",           "CFD Frac.",           False],
      ["preamp_reset_delay_en",  "Preamp Reset En.",    False],   
      ["preamp_reset_delay",     "Preamp Reset",        False],
      ["downsample_factor",      "Downsample",          False],
      ["enable_dec_pause",       "Dec Pause",           False],
      ["trig_ts_mode",           "Trig TS Mode",        False],
      ["Early_pre_m_sel",        "Early Pre-M Capture", False],
      ["MultiplexWordSelect",    "Mux Word Select",     False],
      ["reg_channel_control",    "Control reg",         True ],
    ]

    general_group = QGroupBox("General Settings")
    general_layout = QGridLayout()
    general_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignLeft)
    general_group.setLayout(general_layout)

    self.FillWidgets(general_layout, general_pvNameList, maxRows=13, widgetWidth=100)

    #&================================ External Disc. Settings
    extDisc_pvNameList = [
      ["ext_disc_sel",           "Mode",     False],
      ["ext_disc_src",           "Source",     False]
    ]

    extDisc_group = QGroupBox("Ext. Discr.")
    extDisc_layout = QGridLayout()
    extDisc_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignRight)
    extDisc_group.setLayout(extDisc_layout)

    self.FillWidgets(extDisc_layout, extDisc_pvNameList, maxRows=10, widgetWidth=120)

    #&================================ Window Settings
    window_pvNameList = [
      ["led_threshold",   "Threshold",    False],
      ["k0_window",       "k0",           False],
      ["k_window",        "k",            False],
      ["d_window",        "d",            False],
      ["d3_window",       "d3",           False],
      ["m_window",        "m",            False],
      ["p1_window",       "p1",           False],
      ["p2_window",       "p2",           False],
      ["raw_data_delay",  "Trace Delay",  False],
      ["raw_data_length", "Trace Length", False]
    ]

    window_group = QGroupBox("Window Settings")
    window_layout = QGridLayout()
    window_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignLeft)
    window_group.setLayout(window_layout)

    self.FillWidgets(window_layout, window_pvNameList, maxRows=10, widgetWidth=80)

    self.loadDelaysButton = RSetButton(self.FindPV("load_delays"), "Load Delays", parent=self)
    window_layout.addWidget(self.loadDelaysButton, 10, 0, 1, 2)

    #&================================ Status
    status_pvNameList = [
      ["disc_count",           "Trigger",         False],
      ["ahit_count",           "Accepted Trig.",  False],
      ["accepted_event_count", "Accepted Event",  False],
      ["dropped_event_count",  "Dropped Event",   False],
      ["counter_reset",          "Count Reset",     False],
      ["disc_count_mode",          "",      False],
      ["ahit_count_mode",          "",      False],
      ["event_count_mode",         "",      False],
      ["dropped_event_count_mode", "",      False]
    ]

    status_group = QGroupBox("Status")
    status_layout = QGridLayout()
    status_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignLeft)
    status_group.setLayout(status_layout)

    self.FillWidgets(status_layout, status_pvNameList, maxRows=5, widgetWidth=60)

    #================================= Layout in channel tab
    rowIdx = 1

    layout.addWidget(window_group,  rowIdx    , 0, 1, 2)
    layout.addWidget(status_group,  rowIdx + 1, 0, 2, 2)

    layout.addWidget(general_group, rowIdx    , 2, 2, 1)
    layout.addWidget(extDisc_group, rowIdx + 2, 2, 1, 1)

  #@========================================================  
  def on_channel_changed(self, index):
    if index < 0 or index >= self.board.NumChannels:
      return
    
    self.ch = index

    for pvWidget in self.pvWidgetList:
      new_pv = self.FindChannelPV(self.ch, pvWidget.pv.name.split(":")[-1][:-1])
      pvWidget.pv = new_pv

      if isinstance(pvWidget, RLineEdit):
        pvWidget.setText("")
      else:
        pvWidget.isInitialized = False

  def FillWidgets(self, layout: QGridLayout, pvNameList, maxRows = 9, widgetWidth = 100):
    row = 0
    col = 0

    for pvName, displayName, isHex in pvNameList:
      pv = self.FindChannelPV(self.ch, pvName)
      if pv is not None:
        layout.addWidget(GLabel(displayName, alignment=Qt.AlignmentFlag.AlignRight), row, col)

        if pv.NumStates() > 2:
          pvWidget = RComboBox(pv, width= widgetWidth, parent=self)
        elif pv.NumStates() == 2:
          pvWidget = RTwoStateButton(pv, width= widgetWidth, parent=self)
        else:
          if isHex:
            pvWidget = RLineEdit(pv, hexBinDec="hex", width= widgetWidth, parent=self)
          else:
            pvWidget = RLineEdit(pv, width= widgetWidth, parent=self)

        layout.addWidget(pvWidget, row, col + 1)
        self.pvWidgetList.append(pvWidget)
        row += 1
        if row >= maxRows:
          row = 0
          col += 2

#/###########################################################
class SettingsTabTamplate(ChTabTamplate):
  def __init__(self, board : Board, pvNameList, width = 50, forceUpdate = False, parent=None):
    super().__init__(board, parent)
    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignLeft)

    self.forceUpdate = forceUpdate

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_content = QWidget()
    scroll_layout = QGridLayout(scroll_content)
    scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop| Qt.AlignmentFlag.AlignLeft)
    scroll_content.setLayout(scroll_layout)
    scroll_area.setWidget(scroll_content)
    layout.addWidget(scroll_area, 0, 0, 1, 1)

    self.setLayout(layout)

    rowIdx = 0
    colIdx = 0

    # Populate scroll_layout instead of layout
    for i, (pvName, displayName, _) in enumerate(pvNameList):
      rowIdx = 0
      scroll_layout.addWidget(GLabel(f"{displayName}", alignment=Qt.AlignmentFlag.AlignLeft), rowIdx, colIdx + 1)
      rowIdx += 1

      for ch in range(self.board.NumChannels):
        pv = self.FindChannelPV(ch, pvName)

        if i == 0:
          scroll_layout.addWidget(GLabel(f"{ch}"), rowIdx, colIdx)

        if pv is not None:

          if pv.NumStates() > 2:
            pvWidget = RComboBox(pv, width=width, parent=self)
          elif pv.NumStates() == 2:
            pvWidget = RTwoStateButton(pv, width=width, parent=self)
          else:
            pvWidget = RLineEdit(pv, width=width, parent=self)

          scroll_layout.addWidget(pvWidget, rowIdx, colIdx + 1)
          self.pvWidgetList.append(pvWidget)

        rowIdx += 1

      colIdx += 1

    
  def UpdatePVs(self, forced = False):
    if not self.isVisible():
      return

    super().UpdatePVs(self.forceUpdate)


#^###########################################################################################################
class CHWindow(QMainWindow):
  def __init__(self, board_name, board : Board):
    super().__init__()

    self.ch = 0
    self.board = board

    self.setWindowTitle(board_name)
    self.setGeometry(200, 200,650, 600)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #================================ PV Widgets
    self.pvWidgetList = []

    self.tabWidget = QTabWidget(parent=self)
    layout.addWidget(self.tabWidget, 0, 0, 1, 2)

    channel_tab = ChannelTab(board, parent=self)

    window_pvNameList = [
      ["led_threshold",   "Thresh.",    False],
      ["k0_window",       "k0",           False],
      ["k_window",        "k",            False],
      ["d_window",        "d",            False],
      ["d3_window",       "d3",           False],
      ["m_window",        "m",            False],
      ["p1_window",       "p1",           False],
      ["p2_window",       "p2",           False],
      ["raw_data_delay",  "Trace\nDelay",  False],
      ["raw_data_length", "Trace\nLength", False]
    ]
    windows_tab = SettingsTabTamplate(board, window_pvNameList, parent=self)

    general_pvNameList = [
      ["channel_enable",         "Enable",                False],
      ["trigger_polarity",       "Polarity",              False],
      ["pileup_mode",            "Pileup",                False],
      ["cfd_esum_mode",          "CFD\nE-Sum\nMode",      False],
      ["CFD_fraction",           "CFD\nFrac",             False],
      ["preamp_reset_delay_en",  "Preamp\nReset\nEn.",    False],   
      ["preamp_reset_delay",     "Preamp\nReset",         False],
      ["downsample_factor",      "Down\nSample",          False],
      ["enable_dec_pause",       "Dec\nPause",            False],
      ["trig_ts_mode",           "Trig\nTS\nMode",        False],
      ["Early_pre_m_sel",        "Early\nPre-M\nCapture", False],
      ["MultiplexWordSelect",    "Mux\nWord\nSelect",     False],
      ["reg_channel_control",    "Control\nreg",          True ],
    ]
    general_tab = SettingsTabTamplate(board, general_pvNameList, width=80, parent=self)

    extDisc_pvNameList = [
      ["ext_disc_sel",           "Mode",     False],
      ["ext_disc_src",           "Source",     False]
    ]
    extDisc_tab = SettingsTabTamplate(board, extDisc_pvNameList, width=80, parent=self)

    status_pvNameList = [
      ["channel_enable",       "Enable",           False],
      ["disc_count",           "Trigger",          False],
      ["ahit_count",           "Accepted\nTrig.",  False],
      ["accepted_event_count", "Accepted\nEvent",  False],
      ["dropped_event_count",  "Dropped\nEvent",   False],
      ["counter_reset",        "Count\nReset",     False]
    ]
    status_tab = SettingsTabTamplate(board, status_pvNameList, width=80, forceUpdate=True, parent=self)

    self.tabWidget.addTab(channel_tab, "Channel")
    self.tabWidget.addTab(windows_tab, "Window Settings")
    self.tabWidget.addTab(general_tab, "General Settings")
    self.tabWidget.addTab(extDisc_tab, "Ext. Discr.")
    self.tabWidget.addTab(status_tab, "Status")

    self.tabWidget.currentChanged.connect(lambda _: self.UpdatePVs(forced=True))

    #================================ QTimer for updating PVs
    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second


  #################################################################

  def UpdatePVs(self, forced = False):
    if not self.isVisible():
      return

    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV(forced)

