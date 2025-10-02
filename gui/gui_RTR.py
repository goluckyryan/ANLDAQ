from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget, QGroupBox, QPushButton, QFrame, QComboBox, QLabel
from PyQt6.QtCore import Qt, QTimer

from class_Board import Board
from class_PV import PV
from custom_QClasses import GLabel, GArrow
from class_PVWidgets import RRegisterDisplay, RLineEdit, RTwoStateButton, RComboBox, RMapTwoStateButton, RLabelLineEdit, RSetButton, RMapLineEdit
from gui_RAM import RAMWindow
import re

from aux import make_pattern_list, natural_key

from gui_MTRG import templateTab

############################################################################################################
class rtrlinkControlTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board, parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    rowIdx = 0
    colIdx = 0


    #&================ Create a group box for Link Controls
    link_pv = [ "LOCK",  "DEN",  "REN",  "SYNC", "RPwr", "TPwr", "SLiL", "SLoL", "ILM" , "LINK", "GATED_THROTTLE", "RAW_THROTTLE"]
    link_display = ["Locked", "Drv. En.", "Rec. En", "Sync", "Rx Pwr", "Tx Pwr", "Line Loopback", "Local loopback", "Input Link Mask", "Link", "Gated. Throttle", "Raw Throttle"]
    link_pvList = [[] for _ in range(len(link_pv))]
    link_patterns = make_pattern_list(link_pv)

    for pv in self.board.Board_PV:
      if not isinstance(pv, PV):
        continue
      pvName = pv.name.split(":")[-1]

      if any(re.match(pattern, pvName) for pattern in link_patterns):
        for idx, pattern in enumerate(link_patterns):
          if re.match(pattern, pvName):
            link_pvList[idx].append(pv)  

    groupBox_Link = QGroupBox("Serial/Deserial (SerDes) Links")
    link_layout = QGridLayout()
    link_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_Link.setLayout(link_layout)
    layout.addWidget(groupBox_Link, rowIdx, colIdx, 2, 1 )

    subRowIndex = 0
    for j , link_pv_item in enumerate(link_pv):
      if j  > 0 :
        showColLabel = False
      else:
        showColLabel = True
      
      if len(link_pvList[j]) == 0:
        continue

      link = RMapTwoStateButton(pvList = link_pvList[j], customRowLabel= link_display[j], rowLabelLen=140, rows=1, hasColLabel=showColLabel, cols=len(link_pvList[j]), parent=self)
      if link_pv_item in [ "ILM", "LOCK", "XLM", "YLM"]:
        link.SetInvertStateColor(True)
      link_layout.addWidget(link, subRowIndex, 0)
      self.pvWidgetList.append(link)
      subRowIndex += 1


    #&================ Create LRU
    colIdx = 1
    groupBox_LRU = QGroupBox("LRU Controls")
    lru_layout = QGridLayout()
    lru_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_LRU.setLayout(lru_layout)
    layout.addWidget(groupBox_LRU, rowIdx, colIdx, 1, 1 )

    row = 1
    lru_layout.addWidget(GLabel("Link Init Retry"), row, 0)
    linkInitRetry = RTwoStateButton(self.FindPV("LOCK_RETRY"), width=30, parent=self)
    lru_layout.addWidget(linkInitRetry, row, 1)
    self.pvWidgetList.append(linkInitRetry)

    row += 1
    lru_layout.addWidget(GLabel("Link Init Ack"), row, 0)
    linkInitAck = RTwoStateButton(self.FindPV("LOCK_ACK"), width=30 , parent=self)
    lru_layout.addWidget(linkInitAck, row, 1)
    self.pvWidgetList.append(linkInitAck)

    row += 1
    lru_layout.addWidget(GLabel("Reset Link Init"), row, 0)
    resetLinkInit = RTwoStateButton(self.FindPV("RESET_LINK_INIT"),  width=30, parent=self)
    lru_layout.addWidget(resetLinkInit, row, 1)
    self.pvWidgetList.append(resetLinkInit)

    row += 1
    lru_layout.addWidget(GLabel("LinkStringent"), row, 0)
    linkStringent = RTwoStateButton(self.FindPV("STRINGENT_LOCK"), width=30, parent=self)
    lru_layout.addWidget(linkStringent, row, 1)
    self.pvWidgetList.append(linkStringent)

    row += 1
    lru_layout.addWidget(GLabel("Reset Link Lock"), row, 0)
    resetLinkLock = RTwoStateButton(self.FindPV("SM_LOST_LOCK_RESET"), width=30, parent=self)
    lru_layout.addWidget(resetLinkLock, row, 1)
    self.pvWidgetList.append(resetLinkLock)

                                     
    vline = QFrame()
    vline.setFrameShape(QFrame.Shape.VLine)
    lru_layout.addWidget(vline, 1, 2, 5, 1)

    #------------------ LRU 
    row = 0
    col = 3
    lru_layout.addWidget(GLabel("L", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 1)
    lru_layout.addWidget(GLabel("U", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 2)
    lru_layout.addWidget(GLabel("R", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 3)

    row += 1
    lru_layout.addWidget(GLabel("Drv En."), row, col)
    lsmDrvEn = RTwoStateButton(self.FindPV("LRUCtl00"), width=30, parent=self)
    lsmDrvEn.ClearTxt()
    usmDrvEn = RTwoStateButton(self.FindPV("LRUCtl04"), width=30, parent=self)
    usmDrvEn.ClearTxt()
    rsmDrvEn = RTwoStateButton(self.FindPV("LRUCtl08"), width=30, parent=self)
    rsmDrvEn.ClearTxt()

    lru_layout.addWidget(lsmDrvEn, row, col + 1)
    lru_layout.addWidget(usmDrvEn, row, col + 2)
    lru_layout.addWidget(rsmDrvEn, row, col + 3)

    self.pvWidgetList.append(lsmDrvEn)
    self.pvWidgetList.append(usmDrvEn)
    self.pvWidgetList.append(rsmDrvEn)

    row += 1
    lru_layout.addWidget(GLabel("Rec En."), row, col)
    lsmRecEn = RTwoStateButton(self.FindPV("LRUCtl01"), width=30, parent=self)
    lsmRecEn.ClearTxt()
    usmRecEn = RTwoStateButton(self.FindPV("LRUCtl05"), width=30, parent=self)
    usmRecEn.ClearTxt()
    rsmRecEn = RTwoStateButton(self.FindPV("LRUCtl09"), width=30, parent=self)
    rsmRecEn.ClearTxt()

    lru_layout.addWidget(lsmRecEn, row, col + 1)
    lru_layout.addWidget(usmRecEn, row, col + 2)
    lru_layout.addWidget(rsmRecEn, row, col + 3)

    self.pvWidgetList.append(lsmRecEn)
    self.pvWidgetList.append(usmRecEn)
    self.pvWidgetList.append(rsmRecEn)

    row += 1
    lru_layout.addWidget(GLabel("Sync"), row, col)
    lsmSync = RTwoStateButton(self.FindPV("LRUCtl02"), width=30, parent=self)
    lsmSync.ClearTxt()
    usmSync = RTwoStateButton(self.FindPV("LRUCtl06"), width=30, parent=self)
    usmSync.ClearTxt()
    rsmSync = RTwoStateButton(self.FindPV("LRUCtl10"), width=30, parent=self)
    rsmSync.ClearTxt()

    lru_layout.addWidget(lsmSync, row, col + 1)
    lru_layout.addWidget(usmSync, row, col + 2)
    lru_layout.addWidget(rsmSync, row, col + 3)

    self.pvWidgetList.append(lsmSync)
    self.pvWidgetList.append(usmSync)
    self.pvWidgetList.append(rsmSync)

    row += 1
    lru_layout.addWidget(GLabel("Link L DCbal"), row, col, 1, 2)
    lsmLinkL = RTwoStateButton(self.FindPV("LinkL_DCbal"), width=65, parent=self)
    lru_layout.addWidget(lsmLinkL, row, col + 2, 1, 2)
    self.pvWidgetList.append(lsmLinkL)

    #&========================== Create a group box for Loopback Registers inside groupBox_Link
    groupBox_loopback = QGroupBox("Loopback Registers / LVDS Pre-Emph")
    loopback_layout = QGridLayout()
    loopback_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_loopback.setLayout(loopback_layout)
    layout.addWidget(groupBox_loopback, 1, 1)

    row = 0
    loopback_layout.addWidget(GLabel("Local loopback"), row, 0)
    localLoopback = RLineEdit(self.FindPV("reg_SERDES_LOCAL_LE"), width=60, parent=self)
    loopback_layout.addWidget(localLoopback, row, 1)
    self.pvWidgetList.append(localLoopback)

    loopback_layout.addWidget(GLabel("ABCD"), row, 2)
    preABCD = RTwoStateButton(self.FindPV("PrE_0"), width=40, parent=self)
    self.pvWidgetList.append(preABCD)
    loopback_layout.addWidget(preABCD, row, 3)

    preABCDMode = RComboBox(self.FindPV("PEABCD"), width=80, parent=self)
    self.pvWidgetList.append(preABCDMode)
    loopback_layout.addWidget(preABCDMode, row, 4)

    row += 1
    loopback_layout.addWidget(GLabel("Link loopback"), row, 0)
    linkLoopback = RLineEdit(self.FindPV("reg_SERDES_LINE_LE"), width=60, parent=self)
    loopback_layout.addWidget(linkLoopback, row, 1)
    self.pvWidgetList.append(linkLoopback)

    loopback_layout.addWidget(GLabel("EFG"), row, 2)
    preEFG = RTwoStateButton(self.FindPV("PrE_1"), width=40, parent=self)
    self.pvWidgetList.append(preEFG)
    loopback_layout.addWidget(preEFG, row, 3)

    preEFGMode = RComboBox(self.FindPV("PEEFG"), width=80, parent=self)
    self.pvWidgetList.append(preEFGMode)
    loopback_layout.addWidget(preEFGMode, row, 4)

    row += 1
    loopback_layout.addWidget(GLabel("HLRU"), row, 2)
    preHLRU = RTwoStateButton(self.FindPV("PrE_2"), width=40, parent=self)
    self.pvWidgetList.append(preHLRU)
    loopback_layout.addWidget(preHLRU, row, 3)

    preHLRUMode = RComboBox(self.FindPV("PEHLRU"), width=80, parent=self)
    self.pvWidgetList.append(preHLRUMode)
    loopback_layout.addWidget(preHLRUMode, row, 4)


#@=================================================================
class rtrXYMapTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board, parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    map_pv = ["XMAP_", "YMAP_", "DISCRIMINATOR_DELAY"]
    map_pvList = [[] for _ in range(len(map_pv))]

    for pv in self.board.Board_PV:
      if not isinstance(pv, PV):
        continue
      pvName = pv.name.split(":")[-1]

      for idx, pattern in enumerate(map_pv):
        if pvName.startswith(pattern):
          map_pvList[idx].append(pv)

    layout.addWidget(GLabel("X Map:", alignment=Qt.AlignmentFlag.AlignHCenter), 0, 0)
    xMap = RMapTwoStateButton(pvList = map_pvList[0], parent=self)
    layout.addWidget(xMap, 1, 0)
    self.pvWidgetList.append(xMap)

    layout.addWidget(GLabel("Y Map:", alignment=Qt.AlignmentFlag.AlignHCenter), 0, 1)
    yMap = RMapTwoStateButton(pvList = map_pvList[1], parent=self)
    layout.addWidget(yMap, 1, 1)
    self.pvWidgetList.append(yMap)

    layout.addWidget(GLabel("Discriminator Delay:", alignment=Qt.AlignmentFlag.AlignHCenter), 0, 2)
    ddMap = RMapLineEdit(pvList = map_pvList[2], parent=self)
    layout.addWidget(ddMap, 1, 2)
    self.pvWidgetList.append(ddMap)


    row = 2
    col = 0
    xSel = RComboBox(self.FindPV("X_SELECT"), parent=self)
    layout.addWidget(xSel, row, col)
    self.pvWidgetList.append(xSel)

    col += 1
    ySel = RComboBox(self.FindPV("Y_SELECT"), parent=self)
    layout.addWidget(ySel, row, col)
    self.pvWidgetList.append(ySel)




#^###########################################################################################################
class RTRWindow(QMainWindow):
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

    pvNameList = ["Code_Revision", "CODE_DATE", "reg_TIMESTAMP_A", "reg_TIMESTAMP_B", "reg_TIMESTAMP_C"]
    displayNameList = ["Code Revision", "Code Date", "Timestamp A", "Timestamp B", "Timestamp C"]


    rowIdx = 0
    colIdx = 0
    #&------------------------------ Board Info / Status
    groupBox_info = QGroupBox("Board Info / Status")
    info_layout = QGridLayout()
    info_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_info.setLayout(info_layout)
    layout.addWidget(groupBox_info, rowIdx, colIdx, 1, 1)

    row = 0
    self.miscState = RRegisterDisplay(self.FindPV("reg_MISC_STAT_REG"), True, parent=self)
    info_layout.addWidget(self.miscState, row, 0, 12, 1)

    
    row = 0
    col = 1

    for pvName, displayName in zip( pvNameList, displayNameList):
      pv = self.FindPV(pvName)
      if pv is not None:
        info_layout.addWidget(GLabel(displayName + "  ", alignment=Qt.AlignmentFlag.AlignRight), row, col)
        pvWidget = RLineEdit(pv, hexBinDec="hex", width= 80, parent=self)
        info_layout.addWidget(pvWidget, row, col + 1)
        self.pvWidgetList.append(pvWidget)
        row += 1

    info_layout.addWidget(GLabel("Clock Source  ", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    clockSource = RTwoStateButton( self.FindPV("ClkSrc"), parent=self)
    info_layout.addWidget(clockSource, row, col + 1)
    self.pvWidgetList.append(clockSource)
    row += 1

    #&================ Create a group box for LED Controls
    row += 1
    groupBox_ledControl = QGroupBox("LED Controls")
    led_layout = QGridLayout()
    led_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_ledControl.setLayout(led_layout)
    info_layout.addWidget(groupBox_ledControl, row, 1, 1, 2)

    row = 0
    ledControl = RComboBox(self.FindPV("LEDControl"), parent=self)
    led_layout.addWidget(ledControl, row, 0, 1, 3)
    self.pvWidgetList.append(ledControl)

    row += 1
    led4 = RTwoStateButton(self.FindPV("LED4"), width=30, parent=self)
    led_layout.addWidget(led4, row, 0)
    self.pvWidgetList.append(led4)

    led5 = RTwoStateButton(self.FindPV("LED5"), width=30, parent=self)
    led_layout.addWidget(led5, row, 1)
    self.pvWidgetList.append(led5)

    led6 = RTwoStateButton(self.FindPV("LED6"), width=30, parent=self)
    led_layout.addWidget(led6, row, 2)
    self.pvWidgetList.append(led6)

    row += 1
    led7 = RTwoStateButton(self.FindPV("LED7"), width=30, parent=self)
    led_layout.addWidget(led7, row, 0)
    self.pvWidgetList.append(led7)

    led8 = RTwoStateButton(self.FindPV("LED8"), width=30, parent=self)
    led_layout.addWidget(led8, row, 1)
    self.pvWidgetList.append(led8)

    led9 = RTwoStateButton(self.FindPV("LED9"), width=30, parent=self)
    led_layout.addWidget(led9, row, 2)
    self.pvWidgetList.append(led9)

    row += 1
    led10 = RTwoStateButton(self.FindPV("LED10"), width=30, parent=self)
    led_layout.addWidget(led10, row, 0)
    self.pvWidgetList.append(led10) 

    led11 = RTwoStateButton(self.FindPV("LED11"), width=30, parent=self)
    led_layout.addWidget(led11, row, 1)
    self.pvWidgetList.append(led11)

    led12 = RTwoStateButton(self.FindPV("LED12"), width=30, parent=self)
    led_layout.addWidget(led12, row, 2)
    self.pvWidgetList.append(led12)

    #&------------------------------ Diagnostic
    rowIdx = 0
    colIdx += 1
    groupBox_Diag = QGroupBox("Diagnostic Counters")
    diag_layout = QGridLayout()
    diag_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_Diag.setLayout(diag_layout)
    layout.addWidget(groupBox_Diag, rowIdx, colIdx)

    diagPVList = [pv for pv in self.board.Board_PV if pv.name.split(":")[-1].startswith("reg_Diagnostic")]
    diagPVList.sort(key=lambda x: x.name)
    diagPVDisplayName = ["Type0 Trig", "Type1 Trig", "Type2 Trig", "Type3 Trig", "Type4 Trig", "Rtr Lock Count", "Link L S/D Lock", "Throttle Count"]
    
    row = 0
    for pv, displayName in zip(diagPVList, diagPVDisplayName):
      diag_layout.addWidget(GLabel(displayName, alignment=Qt.AlignmentFlag.AlignRight), row, col)
      pvWidget = RLineEdit(pv, width = 80, parent=self)
      diag_layout.addWidget(pvWidget, row, col+1)
      self.pvWidgetList.append(pvWidget)
      row += 1

    diag_layout.addWidget(GLabel("Throttle Type", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    throttleType = RComboBox(self.FindPV("DIAG_THROTTLE_TYPE"), parent=self)
    diag_layout.addWidget(throttleType, row, col + 1)
    self.pvWidgetList.append(throttleType)

    row += 1
    btnRsetDiag = RSetButton( self.FindPV("CLEAR_DIAG_COUNTERS"), "Clear Counters", parent=self)
    diag_layout.addWidget(btnRsetDiag, row, col, 1, 2)
    self.pvWidgetList.append(btnRsetDiag)

    #&----------------------------- Other Controls
    rowIdx = 0
    colIdx += 1

    groupBox_Other = QGroupBox("Other Controls")
    other_layout = QGridLayout()
    other_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_Other.setLayout(other_layout)
    layout.addWidget(groupBox_Other, rowIdx, colIdx)

    row = 0
    other_layout.addWidget(GLabel("Output Src"), row, 1)

    row += 1
    other_layout.addWidget(GLabel("NIM 1  "), row, 0)
    nim1Src = RComboBox(self.FindPV("NIMSrc1"), parent=self)
    other_layout.addWidget(nim1Src, row, 1)
    self.pvWidgetList.append(nim1Src)

    row += 1
    other_layout.addWidget(GLabel("NIM 2  "), row, 0)
    nim2Src = RComboBox(self.FindPV("NIMSrc2"), parent=self)
    other_layout.addWidget(nim2Src, row, 1)
    self.pvWidgetList.append(nim2Src)

    row += 1 
    other_layout.addWidget(GLabel("NIM Throttle  "), row, 0)
    nimThrottleSrc = RComboBox(self.FindPV("NIM_THROTTLE_SELECT"), parent=self)
    other_layout.addWidget(nimThrottleSrc, row, 1)
    self.pvWidgetList.append(nimThrottleSrc)

    row += 1
    other_layout.addWidget(GLabel("Disc. Delay"), row, 0)
    enableDiscbitDelay = RTwoStateButton(self.FindPV("ENBL_DISCBIT_DELAY"), parent=self)
    other_layout.addWidget(enableDiscbitDelay, row, 1)
    self.pvWidgetList.append(enableDiscbitDelay)

    row += 1 
    other_layout.addWidget(GLabel("Overlap delay [20 ns]"), row, 0)
    overlap = RLineEdit(self.FindPV("OVERLAP_DELAY"), parent=self)
    other_layout.addWidget(overlap, row, 1)
    self.pvWidgetList.append(overlap)

    row += 1
    other_layout.addWidget(GLabel("Assertion delay [20 ns]"), row, 0)
    assertDelay = RLineEdit(self.FindPV("ASSERTION_DELAY"), parent=self)
    other_layout.addWidget(assertDelay, row, 1)
    self.pvWidgetList.append(assertDelay)

    row += 1
    other_layout.addWidget(GLabel("En. Veto"), row, 0)
    enVeto = RTwoStateButton(self.FindPV("ENABLE_VETO"), parent=self)
    enVeto.SetTexts("Off", "On")
    other_layout.addWidget(enVeto, row, 1)
    self.pvWidgetList.append(enVeto)

    row += 1
    other_layout.addWidget(GLabel("Throttle Filter Time"), row, 0)
    throttleFilterTime = RLineEdit(self.FindPV("THROTTLE_FILTER_TIME"), parent=self)
    other_layout.addWidget(throttleFilterTime, row, 1)
    self.pvWidgetList.append(throttleFilterTime)

    row += 1
    other_layout.addWidget(GLabel("Throttle Time Range"), row, 0)
    throttleTimeRange = RComboBox(self.FindPV("THROTTLE_TIME_RANGE"), parent=self)
    other_layout.addWidget(throttleTimeRange, row, 1)
    self.pvWidgetList.append(throttleTimeRange)

    row += 1
    other_layout.addWidget(GLabel("Min Width of Thrtl.\nto MTRG Trig [20 ns]"), row, 0)
    minWidthToMtrg = RLineEdit(self.FindPV("THROTTLE_WIDTH"), parent=self)
    other_layout.addWidget(minWidthToMtrg, row, 1)
    self.pvWidgetList.append(minWidthToMtrg)

    #&------------------------------ Create tabs
    rowIdx += 1
    colIdx = 0
    self.tabs = QTabWidget()
    layout.addWidget(self.tabs, rowIdx, colIdx, 1, 3)

    # Add three tabs
    self.tab1 = rtrlinkControlTab(self.board, parent=self)
    self.tab2 = rtrXYMapTab(self.board, parent=self)

    self.tabs.addTab(self.tab1, "LINK Control")
    self.tabs.addTab(self.tab2, "X/Y Map")

    self.tabs.setCurrentWidget(self.tab1)

    # Connect tab change to force PV update
    self.tabs.currentChanged.connect(lambda idx: self.tabs.widget(idx).UpdatePVs(True)) #force the pv.isUpdate to be False, so that the pv will be displayed.


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
    # if not self.isActiveWindow() or not self.isVisible():
    #   return

    self.miscState.UpdatePV()

    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV()

    current_tab = self.tabs.currentWidget()
    if current_tab is self.tab1:
      self.tab1.UpdatePVs()
    elif current_tab is self.tab2:
      self.tab2.UpdatePVs()
