from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget, QGroupBox, QPushButton
from PyQt6.QtCore import Qt, QTimer

from class_Board import Board
from class_PV import PV
from custom_QClasses import GLabel
from class_PVWidgets import RRegisterDisplay, RLineEdit, RTwoStateButton, RComboBox, RMapTwoStateButton, RLabelLineEdit, RSetButton
from gui_RAM import RAMWindow
import re

############################################################################################################
class templateTab(QWidget):
  def __init__(self, board : Board, parent=None):
    super().__init__(parent)
    self.board = board
    self.pvWidgetList = []


  def UpdatePVs(self):
    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV()


  def FindPV(self, pv_name) -> PV:
    for pv in self.board.Board_PV:
      pvName = pv.name.split(":")[-1]
      if pvName == pv_name:
        return pv
    return None


#------------------------------------------------------------------------------------------------------------
class triggerControlTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board, parent)
    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    layout.addWidget(GLabel("Trigger Control Settings will be here"), 0, 0)

  

#------------------------------------------------------------------------------------------------------------
class linkControlTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board,parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)


    layout.addWidget(GLabel("Link Control Settings will be here"), 0, 0)

#------------------------------------------------------------------------------------------------------------
class otherControlTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board, parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    #================ Create a group box for NIM Output Controls
    groupBox_nimOutput = QGroupBox("NIM Output Controls")
    nim_layout = QGridLayout()
    nim_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_nimOutput.setLayout(nim_layout)
    layout.addWidget(groupBox_nimOutput, 0, 0, 1, 5)

    row = 0
    nim_layout.addWidget(GLabel("Output Src"), row, 1)
    nim_layout.addWidget(GLabel("Sub Src"), row, 2)
    nim_layout.addWidget(GLabel("En. Delay"), row, 3)
    nim_layout.addWidget(GLabel("Delay * 20 ns"), row, 4)

    row += 1
    nim_layout.addWidget(GLabel("NIM 1  "), row, 0)
    nim1Src = RComboBox(self.FindPV("NIMSrc1"), parent=self)
    nim1Sub = RComboBox(self.FindPV("NIM1_SubSelect"), parent=self)
    nim1InputDelayEnable = RTwoStateButton(self.FindPV("EN_NIM1_DELAY"), parent=self)
    nim1InputDelay = RLineEdit(self.FindPV("reg_NIM1_DELAY"), parent=self)
    nim1Src.currentIndexChanged.connect(lambda idx: nim1Sub.setEnabled(idx == 0))
    nim1Src.whenIndexZero.connect(lambda enable: nim1Sub.setEnabled(enable))
    nim1InputDelayEnable.stateChanged.connect(lambda state: nim1InputDelay.setEnabled(state))

    nim_layout.addWidget(nim1Src, row, 1)
    nim_layout.addWidget(nim1Sub, row, 2)
    nim_layout.addWidget(nim1InputDelayEnable, row, 3)
    nim_layout.addWidget(nim1InputDelay, row, 4)

    self.pvWidgetList.append(nim1Src)
    self.pvWidgetList.append(nim1Sub)
    self.pvWidgetList.append(nim1InputDelayEnable)
    self.pvWidgetList.append(nim1InputDelay)

    row += 1
    nim_layout.addWidget(GLabel("NIM 2  "), row, 0)
    nim2Src = RComboBox(self.FindPV("NIMSrc2"), parent=self)
    nim2Sub = RComboBox(self.FindPV("NIM2_SubSelect"), parent=self)
    nim2InputDelayEnable = RTwoStateButton(self.FindPV("EN_NIM2_DELAY"), parent=self)
    nim2InputDelay = RLineEdit(self.FindPV("reg_NIM2_DELAY"), parent=self)
    nim2Src.currentIndexChanged.connect(lambda idx: nim2Sub.setEnabled(idx == 0))
    nim2Src.whenIndexZero.connect(lambda enable: nim2Sub.setEnabled(enable))
    nim2InputDelayEnable.stateChanged.connect(lambda state: nim2InputDelay.setEnabled(state))


    nim_layout.addWidget(nim2Src, row, 1)
    nim_layout.addWidget(nim2Sub, row, 2)
    nim_layout.addWidget(nim2InputDelayEnable, row, 3)
    nim_layout.addWidget(nim2InputDelay, row, 4)

    self.pvWidgetList.append(nim2Src)
    self.pvWidgetList.append(nim2Sub)
    self.pvWidgetList.append(nim2InputDelayEnable)
    self.pvWidgetList.append(nim2InputDelay)

    #================ Create a group box for Trigger Data Readout
    groupBox_trigData = QGroupBox("Trigger Data Readout")
    trigData_layout = QGridLayout()
    trigData_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_trigData.setLayout(trigData_layout)
    layout.addWidget(groupBox_trigData, 1, 0, 1, 5)

    row = 0
    trigData_layout.addWidget(GLabel("Src  "), row, 0)
    dataSrc = RComboBox(self.FindPV("TRIG_MON_SEL"), parent=self)
    dataSrc.setFixedWidth(120)
    trigData_layout.addWidget(dataSrc, row, 1)    
    self.pvWidgetList.append(dataSrc)

    trigData_layout.addWidget(GLabel("E"), row, 3)
    trigData_layout.addWidget(GLabel("AE"), row, 4)
    trigData_layout.addWidget(GLabel("AF"), row, 5)
    trigData_layout.addWidget(GLabel("F"), row, 6)

    row += 1
    trigData_layout.addWidget(GLabel("Skip  "), row, 0)
    skipEna = RTwoStateButton(self.FindPV("SKIP_TDC_DATA"), parent=self)
    skipEna.setFixedWidth(120)
    trigData_layout.addWidget(skipEna, row, 1)
    self.pvWidgetList.append(skipEna)

    stateEmpty = RTwoStateButton(self.FindPV("Mon_7_FIFO_Empty"), parent=self)
    stateAlmostEmpty = RTwoStateButton(self.FindPV("Mon_7_FIFO_Almost_Empty"), parent=self)
    stateAlmostFull = RTwoStateButton(self.FindPV("Mon_7_FIFO_Almost_Full"), parent=self)
    stateFull = RTwoStateButton(self.FindPV("Mon_7_FIFO_Full"), parent=self)

    trigData_layout.addWidget(stateEmpty, row, 3)
    trigData_layout.addWidget(stateAlmostEmpty, row, 4)
    trigData_layout.addWidget(stateAlmostFull, row, 5)
    trigData_layout.addWidget(stateFull, row, 6)

    stateEmpty.ClearTxt()
    stateAlmostEmpty.ClearTxt()
    stateAlmostFull.ClearTxt()
    stateFull.ClearTxt()

    stateEmpty.setFixedWidth(20)
    stateAlmostEmpty.setFixedWidth(20)
    stateAlmostFull.setFixedWidth(20)
    stateFull.setFixedWidth(20)

    self.pvWidgetList.append(stateEmpty)
    self.pvWidgetList.append(stateAlmostEmpty)
    self.pvWidgetList.append(stateAlmostFull)
    self.pvWidgetList.append(stateFull)

    row += 1
    trigData_layout.addWidget(GLabel("En. Fifo Mon  "), row, 0)
    fifoMonEna = RTwoStateButton(self.FindPV("SYSMON_ENABLE"), parent=self)
    trigData_layout.addWidget(fifoMonEna, row, 1)
    self.pvWidgetList.append(fifoMonEna)

    resetFifo = RTwoStateButton(self.FindPV("reg_FIFO_RESETS"), parent=self)
    resetFifo.SetTexts("Normal", "Reset")
    resetFifo.SetInvertStateColor(True)
    trigData_layout.addWidget(resetFifo, row, 2)
    self.pvWidgetList.append(resetFifo)

    fifoCount = RLineEdit(self.FindPV("reg_MON7_FIFO_DEPTH"), parent=self)
    fifoCount.setFixedWidth(100)
    trigData_layout.addWidget(fifoCount, row, 3, 1, 4)
    self.pvWidgetList.append(fifoCount)



############################################################################################################
class MTRGWindow(QMainWindow):
  def __init__(self, board_name, board : Board):
    super().__init__()

    self.board = board

    self.setWindowTitle(board_name)
    self.setGeometry(150, 150, 600, 600)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #------------------------------ PV Widgets
    self.pvWidgetList = []

    pvNameList = ["reg_CODE_REVISION", "reg_CODE_DATE", "reg_TIMESTAMP_A", "reg_TIMESTAMP_B", "reg_TIMESTAMP_C"]
    displayNameList = ["Code Revision", "Code Date", "Timestamp A", "Timestamp B", "Timestamp C"]

    diagPVList = [pv for pv in self.board.Board_PV if pv.name.split(":")[-1].startswith("reg_Diagnostic")]
    diagPVList.sort(key=lambda x: x.name)
    diagPVDisplayName = ["Man/Aux Trigs", "Sum X Trigs", "Sum Y Trigs", "Sum XY Trigs", "CPLD Trigs", "Link L Locks", "Nim 1 Trigs", "Nim 2 Trigs"]
    
    trigRateHighPVList = [
      pv for pv in self.board.Board_PV
      if re.match(r'reg_RAW_TRIG_RATE_COUNTER_\d_HIGH$', pv.name.split(":")[-1])
    ]
    trigRateHighPVList.sort(key=lambda x: x.name)
    trigRateLowPVList = [
      pv for pv in self.board.Board_PV
      if re.match(r'reg_RAW_TRIG_RATE_COUNTER_\d_LOW$', pv.name.split(":")[-1])
    ]
    trigRateLowPVList.sort(key=lambda x: x.name)

    accptTrigHighPVList = [
      pv for pv in self.board.Board_PV
      if re.match(r'reg_TRIG_RATE_COUNTER_\d_HIGH$', pv.name.split(":")[-1])
    ]
    accptTrigHighPVList.sort(key=lambda x: x.name)
    accptTrigLowPVList = [
      pv for pv in self.board.Board_PV
      if re.match(r'reg_TRIG_RATE_COUNTER_\d_LOW$', pv.name.split(":")[-1])
    ]
    accptTrigLowPVList.sort(key=lambda x: x.name)


    rowIdx = 0
    colIdx = 0
    #------------------------------ Board Info / Status
    groupBox_info = QGroupBox("Board Info / Status")
    info_layout = QGridLayout()
    info_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_info.setLayout(info_layout)
    layout.addWidget(groupBox_info, rowIdx, colIdx, 1, 1)

    row = 0
    self.miscState = RRegisterDisplay(self.FindPV("reg_MISC_STAT"), True, parent=self)
    info_layout.addWidget(self.miscState, row, 0, 12, 1)

    
    row = 0
    col = 1

    for pvName, displayName in zip( pvNameList, displayNameList):
      pv = self.FindPV(pvName)
      if pv is not None:
        info_layout.addWidget(GLabel(displayName + "  ", alignment=Qt.AlignmentFlag.AlignRight), row, col)
        pvWidget = RLineEdit(pv, isHex=True, parent=self)
        info_layout.addWidget(pvWidget, row, col + 1)
        self.pvWidgetList.append(pvWidget)
        row += 1

    info_layout.addWidget(GLabel("Clock Source  ", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    clockSource = RTwoStateButton( self.FindPV("ClkSrc"), parent=self)
    info_layout.addWidget(clockSource, row, col + 1)
    self.pvWidgetList.append(clockSource)
    row += 1

    info_layout.addWidget(GLabel("Imp Sync  ", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    impSync = RTwoStateButton( self.FindPV("IMP_SYNC"), parent=self)
    info_layout.addWidget(impSync, row, col + 1)
    self.pvWidgetList.append(impSync)
    row += 1


    #------------------------------ Trigger Rate Counters
    rowIdx = 0
    colIdx += 1
    groupBox_trigRate = QGroupBox("Trigger Rate Counters")
    trigRate_layout = QGridLayout()
    trigRate_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_trigRate.setLayout(trigRate_layout)
    layout.addWidget(groupBox_trigRate, rowIdx, colIdx)

    row = 0
    col = 0
    trigRate_layout.addWidget(GLabel("Raw", alignment=Qt.AlignmentFlag.AlignCenter), row, col + 1, 1, 2)
    row += 1
    trigRate_layout.addWidget(GLabel("High", alignment=Qt.AlignmentFlag.AlignCenter), row, col + 1)
    trigRate_layout.addWidget(GLabel("Low", alignment=Qt.AlignmentFlag.AlignCenter), row, col + 2)
    row += 1

    for idx, (highPV, lowPV) in enumerate(zip(trigRateHighPVList, trigRateLowPVList), start=1):
      trigRate_layout.addWidget(GLabel(str(idx)), row, col)
      highWidget = RLineEdit(highPV, width=60, parent=self)
      lowWidget = RLineEdit(lowPV, width=60, parent=self)
      trigRate_layout.addWidget(highWidget, row, col + 1)
      trigRate_layout.addWidget(lowWidget, row, col + 2)
      self.pvWidgetList.append(highWidget)
      self.pvWidgetList.append(lowWidget)
      row += 1

    btnResetRate = RSetButton( self.FindPV("CLEAR_RATE_COUNTERS"), "Clear Rate", parent=self)
    trigRate_layout.addWidget(btnResetRate, row, col +1, 1, 2)
  
    row = 0
    col = 4
    trigRate_layout.addWidget(GLabel("Accepted", alignment=Qt.AlignmentFlag.AlignCenter), row, col + 1, 1, 2)
    row += 1
    trigRate_layout.addWidget(GLabel("High", alignment=Qt.AlignmentFlag.AlignCenter), row, col + 1)
    trigRate_layout.addWidget(GLabel("Low", alignment=Qt.AlignmentFlag.AlignCenter), row, col + 2)
    row += 1 
    for idx, (highPV, lowPV) in enumerate(zip(accptTrigHighPVList, accptTrigLowPVList), start=1):
      trigRate_layout.addWidget(GLabel(str(idx)), row, col)
      highWidget = RLineEdit(highPV,width=60, parent=self)
      lowWidget = RLineEdit(lowPV, width=60, parent=self)
      trigRate_layout.addWidget(highWidget, row, col + 1)
      trigRate_layout.addWidget(lowWidget, row, col + 2)
      self.pvWidgetList.append(highWidget)
      self.pvWidgetList.append(lowWidget)
      row += 1
  
    btnCounterMode = RTwoStateButton( self.FindPV("Trigger_rate_counter_mode"), parent=self)
    trigRate_layout.addWidget(btnCounterMode, row, col + 1, 1, 2)
    self.pvWidgetList.append(btnCounterMode)

    row = 1
    col = 7
    trigRate_layout.addWidget(GLabel("Diagnostic", alignment=Qt.AlignmentFlag.AlignCenter), row, col, 1, 2)
    row += 1

    for pv, displayName in zip(diagPVList, diagPVDisplayName):
      trigRate_layout.addWidget(GLabel(displayName, alignment=Qt.AlignmentFlag.AlignRight), row, col)
      pvWidget = RLineEdit(pv, width = 60, parent=self)
      trigRate_layout.addWidget(pvWidget, row, col+1)
      self.pvWidgetList.append(pvWidget)
      row += 1

    btnRsetDiag = RSetButton( self.FindPV("CLEAR_DIAG_COUNTERS"), "Clear Counters", parent=self)
    trigRate_layout.addWidget(btnRsetDiag, row, col, 1, 2)
    self.pvWidgetList.append(btnRsetDiag)

    #------------------------------ Create tabs
    rowIdx += 1
    colIdx = 0
    self.tabs = QTabWidget()
    layout.addWidget(self.tabs, rowIdx, colIdx, 1, 2)

    # Add three tabs
    self.tab1 = triggerControlTab(self.board, parent=self)
    self.tab2 = linkControlTab(self.board, parent=self)
    self.tab3 = otherControlTab(self.board, parent=self)

    self.tabs.addTab(self.tab1, "Trigger Control")
    self.tabs.addTab(self.tab2, "Link Control")
    self.tabs.addTab(self.tab3, "Other Control")

    #------------------------------ QTimer for updating PVs
    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second

  #################################################################
  def FindPV(self, pv_name) -> PV:
    for pv in self.board.Board_PV:
      pvName = pv.name.split(":")[-1]
      if pvName == pv_name:
        return pv
    return None
  
  def UpdatePVs(self):
    self.miscState.UpdatePV()

    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV()

    # Only update the tab that is currently active
    current_tab = self.tabs.currentWidget()
    if current_tab is self.tab1:
      self.tab1.UpdatePVs()
    elif current_tab is self.tab2:
      self.tab2.UpdatePVs()
    elif current_tab is self.tab3:
      self.tab3.UpdatePVs()
