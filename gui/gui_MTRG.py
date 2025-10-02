from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget, QGroupBox, QPushButton, QFrame, QComboBox, QLabel
from PyQt6.QtCore import Qt, QTimer

from class_Board import Board
from class_PV import PV
from custom_QClasses import GLabel, GArrow
from class_PVWidgets import RRegisterDisplay, RLineEdit, RTwoStateButton, RComboBox, RMapTwoStateButton, RLabelLineEdit, RSetButton
from gui_RAM import RAMWindow
import re

from aux import make_pattern_list, natural_key


############################################################################################################
class templateTab(QWidget):
  def __init__(self, board : Board, parent=None):
    super().__init__(parent)
    self.board = board
    self.pvWidgetList = []


  def UpdatePVs(self, forced = False):
    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV(forced)


  def FindPV(self, pv_name) -> PV:
    for pv in self.board.Board_PV:
      pvName = pv.name.split(":")[-1]
      if pvName == pv_name:
        return pv
    return None


#@========================================================================================
class triggerControlTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board, parent)
    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    #--------------------- header
    row = 0
    layout.addWidget(GLabel("VETO", alignment=Qt.AlignmentFlag.AlignHCenter), row, 5, 1, 3)
    layout.addWidget(GLabel("Trigger Prescale", alignment=Qt.AlignmentFlag.AlignHCenter), row, 9, 1, 2)

    row += 1
    layout.addWidget(GLabel("En.", alignment=Qt.AlignmentFlag.AlignHCenter), row, 3)
    layout.addWidget(GLabel("NIM", alignment=Qt.AlignmentFlag.AlignHCenter), row, 5)
    layout.addWidget(GLabel("Thrtl", alignment=Qt.AlignmentFlag.AlignHCenter), row, 6)
    layout.addWidget(GLabel("RAM", alignment=Qt.AlignmentFlag.AlignHCenter), row, 7)

    layout.addWidget(GLabel("En.", alignment=Qt.AlignmentFlag.AlignHCenter), row, 9)
    layout.addWidget(GLabel("Factor", alignment=Qt.AlignmentFlag.AlignHCenter), row, 10)

    # Add vertical line after col 3
    vline = QFrame()
    vline.setFrameShape(QFrame.Shape.VLine)
    # vline.setFrameShadow(QFrame.Shadow.Sunken)
    layout.addWidget(vline, 2, 4, 8, 1)  # span enough rows

    vline2 = QFrame()
    vline2.setFrameShape(QFrame.Shape.VLine)
    layout.addWidget(vline2, 2, 8, 11, 1)  # span enough rows

    vline3 = QFrame()
    vline3.setFrameShape(QFrame.Shape.VLine)
    layout.addWidget(vline3, 2, 11, 8, 1)  # span enough rows

    row += 1
    enNIM = RTwoStateButton(self.FindPV("EN_NIM_AUX"), width=80, parent=self)
    enNIM.SetTexts("NIM Dis.", "NIM En.")
    self.pvWidgetList.append(enNIM)
    layout.addWidget(enNIM, row, 0)

    enRAM = RTwoStateButton(self.FindPV("EN_TRIG_RAM_AUX"), width=80, parent=self)
    enRAM.SetTexts("RAM Dis.", "RAM En.")
    self.pvWidgetList.append(enRAM)
    layout.addWidget(enRAM, row, 1)

    row += 1
    layout.addWidget(GLabel("X-Threshold "), row, 0)
    xThreshold = RLineEdit(self.FindPV("reg_SUM_OF_X_THRESH"), width=80, parent=self)
    self.pvWidgetList.append(xThreshold)
    layout.addWidget(xThreshold, row, 1)

    row += 1
    layout.addWidget(GLabel("Y-Threshold "), row, 0)
    yThreshold = RLineEdit(self.FindPV("reg_SUM_OF_Y_THRESH"), width=80, parent=self)
    self.pvWidgetList.append(yThreshold)
    layout.addWidget(yThreshold, row, 1)


    #*-------------------------- trigger controls

    pvNameList = ["EN_MAN_AUX", "EN_SUM_X", "EN_SUM_Y", "EN_SUM_XY", "EN_ALGO5", "EN_LINK_L", "EN_LINK_R", "EN_MYRIAD_LINK_U"]
    displayNameList = ["MAX/AUX/NIM", "SUM X", "SUM Y", "SUM XY", "CPLD/Coinc", "LINK L", "LINK R", "MYRIAD/LINK U"]

    nim_veto_pv_list = [ pv for pv in self.board.Board_PV if pv.name.split(":")[-1].startswith("EN_NIM_VETO_")]
    thrl_veto_pv_list = [ pv for pv in self.board.Board_PV if pv.name.split(":")[-1].startswith("EN_THROTTLE_VETO_")]
    ram_veto_pv_list = [ pv for pv in self.board.Board_PV if pv.name.split(":")[-1].startswith("EN_RAM_VETO_")]

    prescaleEn_pv_list = [
      pv for pv in self.board.Board_PV
      if re.match(r'TRIG_[A-Z]_PRESCALE_ENBL$', pv.name.split(":")[-1])
    ]
    prescaleEn_pv_list.sort(key=lambda x: x.name)

    prescaleFactor_pv_list = [
      pv for pv in self.board.Board_PV
      if re.match(r'TRIG_[A-Z]_PRESCALE_FACTOR$', pv.name.split(":")[-1])
    ]
    prescaleFactor_pv_list.sort(key=lambda x: x.name)


    row = 2
    col = 2
    for i, (pvName, displayName) in enumerate(zip(pvNameList, displayNameList)):
      layout.addWidget(GLabel(displayName + "  ", alignment=Qt.AlignmentFlag.AlignRight), row, col)
      pvWidget = RTwoStateButton(self.FindPV(pvName), width = 30, parent=self)
      pvWidget.ClearTxt()
      layout.addWidget(pvWidget, row, col + 1)
      self.pvWidgetList.append(pvWidget)

      nim_pv_widget = RTwoStateButton(nim_veto_pv_list[i], width = 30, parent=self)
      nim_pv_widget.ClearTxt()
      layout.addWidget(nim_pv_widget, row, col + 3)
      self.pvWidgetList.append(nim_pv_widget)

      thrl_pv_widget = RTwoStateButton(thrl_veto_pv_list[i], width = 30, parent=self)
      thrl_pv_widget.ClearTxt()
      layout.addWidget(thrl_pv_widget, row, col + 4)
      self.pvWidgetList.append(thrl_pv_widget)

      ram_pv_widget = RTwoStateButton(ram_veto_pv_list[i], width = 30, parent=self)
      ram_pv_widget.ClearTxt()
      layout.addWidget(ram_pv_widget, row, col + 5)
      self.pvWidgetList.append(ram_pv_widget)

      prescale_pv_widget = RTwoStateButton(prescaleEn_pv_list[i], width = 30, parent=self)
      prescale_pv_widget.ClearTxt()
      layout.addWidget(prescale_pv_widget, row, col + 7)
      self.pvWidgetList.append(prescale_pv_widget)

      prescaleFactor_widget = RLineEdit(prescaleFactor_pv_list[i], width=80, parent=self)
      layout.addWidget(prescaleFactor_widget, row, col + 8)
      self.pvWidgetList.append(prescaleFactor_widget)


      row += 1

    #*-------------------------- total veto controls
    layout.addWidget(GLabel("Veto Ctrl.  "), row, col, 1, 3)

    nim_veto_widget = RTwoStateButton(self.FindPV("ENBL_NIM_VETO"), width=30, parent=self)
    nim_veto_widget.ClearTxt()
    layout.addWidget(nim_veto_widget, row, col+3)
    self.pvWidgetList.append(nim_veto_widget)

    thrl_veto_widget = RTwoStateButton(self.FindPV("ENBL_THROTTLE_VETO"), width=30, parent=self)
    thrl_veto_widget.ClearTxt()
    layout.addWidget(thrl_veto_widget, row, col+4)
    self.pvWidgetList.append(thrl_veto_widget)

    ram_veto_widget = RTwoStateButton(self.FindPV("EN_RAM_VETO"), width=30, parent=self)
    ram_veto_widget.ClearTxt()
    layout.addWidget(ram_veto_widget, row, col+5)
    self.pvWidgetList.append(ram_veto_widget)
    

    row += 1
    layout.addWidget(GLabel("Software Veto  "), row, col, 1, 5)
    swTrig = RTwoStateButton(self.FindPV("SOFTWARE_VETO"), width=30, parent=self)
    swTrig.ClearTxt()
    layout.addWidget(swTrig, row, col + 5)
    self.pvWidgetList.append(swTrig)

    row += 1
    layout.addWidget(GLabel("Mon 7 Veto  "), row, col, 1, 5)
    mon7Veto = RTwoStateButton(self.FindPV("ENBL_MON7_VETO"), width=30, parent=self)
    mon7Veto.ClearTxt()
    layout.addWidget(mon7Veto, row, col + 5)
    self.pvWidgetList.append(mon7Veto)


    row = 6
    col = 0
    aglo5_sele_widget = RTwoStateButton(self.FindPV("ALGO_5_SELECT"), parent=self, color="")
    layout.addWidget(aglo5_sele_widget, row, col, 1, 2)
    self.pvWidgetList.append(aglo5_sele_widget)

    row = 9
    linkU_sele_widget = RTwoStateButton(self.FindPV("LINK_U_IS_TRIGGER_TYPE"), parent=self, color="") 
    layout.addWidget(linkU_sele_widget, row, col, 1, 2)
    self.pvWidgetList.append(linkU_sele_widget)

    row = 10
    myriad_sele_widget = RTwoStateButton(self.FindPV("MYR_TRIGGER_TYPE_SELECT"), parent=self, color="")
    myriad_sele_widget.SetTexts("Myriad Raw", "Myriad Gated")
    layout.addWidget(myriad_sele_widget, row, col, 1, 2)
    self.pvWidgetList.append(myriad_sele_widget)

    #*-------------------------- coincidence frame
    row = 0
    col = 12
    layout.addWidget(GLabel("Coinc. Masks"), row, col-1, 1, 3)

    row = 1
    layout.addWidget(GLabel("A", alignment=Qt.AlignmentFlag.AlignHCenter), row, col)
    layout.addWidget(GLabel("B", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 1)


    coinTrigMaskA_pv_list = [ pv for pv in self.board.Board_PV if pv.name.split(":")[-1].startswith("COINC_TRIG_MASK_A")]
    coinTrigMaskB_pv_list = [ pv for pv in self.board.Board_PV if pv.name.split(":")[-1].startswith("COINC_TRIG_MASK_B")]

    row = 2
    for i in range(len(coinTrigMaskA_pv_list)):
      if i == 4 :
        row += 1

      coinMaskA_widget = RTwoStateButton(coinTrigMaskA_pv_list[i], width=30, parent=self)
      coinMaskA_widget.ClearTxt()
      layout.addWidget(coinMaskA_widget, row, col)
      self.pvWidgetList.append(coinMaskA_widget)

      coinMaskB_widget = RTwoStateButton(coinTrigMaskB_pv_list[i], width=30, parent=self)
      coinMaskB_widget.ClearTxt()
      layout.addWidget(coinMaskB_widget, row, col + 1)
      self.pvWidgetList.append(coinMaskB_widget)

      row += 1

    row = 10 
    layout.addWidget(GLabel("Coinc. Overlap * 20 ns"), row, 9, 1, 3)
    overlapTime_widget = RLineEdit(self.FindPV("COINC_OVERLAP_DELAY"), width = 70, parent=self)
    layout.addWidget(overlapTime_widget, row, 12, 1, 2)
    self.pvWidgetList.append(overlapTime_widget)

    #*-------------------------- propagation frame
    row = 7

    layout.addWidget(GLabel("Propagation Frames", alignment=Qt.AlignmentFlag.AlignHCenter), row - 2, 15, 1, 6)

    frameList = ["F1", "F3", "F4", "F5", "F6", "F7"]
    # Find all PVs with pattern "LINK_Y_PROPAGATE_XX", where Y in ["L", "R", "U"] and XX in frameList
    frameL_pv_list = [pv for pv in self.board.Board_PV if re.match(rf'LINK_L_PROPAGATE_({"|".join(frameList)})$', pv.name.split(":")[-1])]
    frameR_pv_list = [pv for pv in self.board.Board_PV if re.match(rf'LINK_R_PROPAGATE_({"|".join(frameList)})$', pv.name.split(":")[-1])]
    frameU_pv_list = [pv for pv in self.board.Board_PV if re.match(rf'LINK_U_PROPAGATE_({"|".join(frameList)})$', pv.name.split(":")[-1])]

    vline4 = QFrame()
    vline4.setFrameShape(QFrame.Shape.VLine)
    layout.addWidget(vline4, row, 14, 3, 1)  # span enough rows

    for i , pv in enumerate(frameL_pv_list):
      layout.addWidget(GLabel(frameList[i], alignment=Qt.AlignmentFlag.AlignHCenter), row - 1, 15 + i)
      frameL_widget = RTwoStateButton(pv, width=30, parent=self)
      frameL_widget.ClearTxt()
      layout.addWidget(frameL_widget, row, 15 + i)
      self.pvWidgetList.append(frameL_widget)

      if i == 0 :
        continue

      frameR_widget = RTwoStateButton(frameR_pv_list[i], width=30, parent=self)
      frameR_widget.ClearTxt()
      layout.addWidget(frameR_widget, row + 1, 15 + i)
      self.pvWidgetList.append(frameR_widget)

      frameU_widget = RTwoStateButton(frameU_pv_list[i], width=30, parent=self)
      frameU_widget.ClearTxt()
      layout.addWidget(frameU_widget, row + 2, 15 + i)
      self.pvWidgetList.append(frameU_widget)
      
    

#@========================================================================================
class wheelRAMTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board,parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    #*-------------------------- AUX I/O Group Box
    rowIdx = 0
    colIdx = 0

    groupBox_auxIO = QGroupBox("AUX I/O")
    auxio_layout = QGridLayout()
    auxio_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_auxIO.setLayout(auxio_layout)
    layout.addWidget(groupBox_auxIO, rowIdx, colIdx, 6, 4)

    # Direction labels and buttons
    row = 0
    auxio_layout.addWidget(GLabel("Direction"), row, 0, 1, 2)
    auxio_layout.addWidget(GLabel("Bits 15:12"), row+1, 0)
    auxio_layout.addWidget(GLabel("Bits 11:8"), row+2, 0)
    auxio_layout.addWidget(GLabel("Bits 7:4"), row+3, 0)
    auxio_layout.addWidget(GLabel("Bits 3:0"), row+4, 0)

    bitA = RTwoStateButton(self.FindPV("A_7_4_DIR"), width=70, parent=self)
    bitB = RTwoStateButton(self.FindPV("A_3_0_DIR"), width=70, parent=self)
    bitC = RTwoStateButton(self.FindPV("B_7_4_DIR"), width=70, parent=self)
    bitD = RTwoStateButton(self.FindPV("B_3_0_DIR"), width=70, parent=self)

    auxio_layout.addWidget(bitA, row + 1, 1)
    auxio_layout.addWidget(bitB, row + 2, 1)
    auxio_layout.addWidget(bitC, row + 3, 1)
    auxio_layout.addWidget(bitD, row + 4, 1)

    self.pvWidgetList.append(bitA)
    self.pvWidgetList.append(bitB)
    self.pvWidgetList.append(bitC)
    self.pvWidgetList.append(bitD)

    # Serial/Parallel selection
    row = 1
    col = 2
    serialOrParallel = RTwoStateButton(self.FindPV("SSI_ENABLE"), width=100, parent=self)
    serialOrParallel.SetTexts("Serial", "Parallel")
    serialOrParallel.setMaximumHeight(100)
    serialOrParallel.stateChanged.connect(self.onSerialOrParallelChanged)
    auxio_layout.addWidget(serialOrParallel, row, col, 4, 1)
    self.pvWidgetList.append(serialOrParallel)

    # SSI Input and Polarity
    col = 3
    row = 2
    self.ssiInput = RComboBox(self.FindPV("SSI_InputSelect"), width=100, parent=self)
    auxio_layout.addWidget(self.ssiInput, row, col, 1, 1)
    self.pvWidgetList.append(self.ssiInput)

    self.polarity = RTwoStateButton(self.FindPV("AUXPolaritySelect"), parent=self)
    auxio_layout.addWidget(self.polarity, row + 1, col, 1, 2)
    self.pvWidgetList.append(self.polarity)

    # Transmission Length
    col = 4
    row = 1
    auxio_layout.addWidget(GLabel("Trans. Len. [bit]"), row, col, 1, 1, alignment=Qt.AlignmentFlag.AlignBottom)
    self.ssiTransLen = RLineEdit(self.FindPV("SSI_TransLen"), width=100, parent=self)
    auxio_layout.addWidget(self.ssiTransLen, row + 1, col, 1, 1)
    self.pvWidgetList.append(self.ssiTransLen)

    # Encode Filter Time
    col = 5
    row = 0
    auxio_layout.addWidget(GLabel("Encode\nFilter Time"), row, col, 3, 1)
    encodeFilterTime = RLineEdit(self.FindPV("EncFilterTimePHYS"), width=100, parent=self)
    self.pvWidgetList.append(encodeFilterTime)
    auxio_layout.addWidget(encodeFilterTime, row + 2, col, 2, 1)


    #*-------------------------- Other Controls
    rowIdx = 6
    colIdx = 3
    layout.addWidget(GLabel("Manual Data"), rowIdx, colIdx, 1, 1)
    manualData = RLineEdit(self.FindPV("ENCODER_MANUAL_DATA"), width=100, parent=self)
    self.pvWidgetList.append(manualData)
    layout.addWidget(manualData, rowIdx + 1, colIdx, 1, 1)

    rowIdx = 8
    layout.addWidget(GLabel("Int. Freq."), rowIdx, colIdx, 1, 1)
    intFreq = RComboBox(self.FindPV("SLOW_CLOCK_SEL"), width=100, parent=self)
    self.pvWidgetList.append(intFreq)
    layout.addWidget(intFreq, rowIdx + 1, colIdx, 1, 1)

    roll99 = RTwoStateButton(self.FindPV("COUNTER_ROLL_999"), width=100, parent=self)
    roll99.SetTexts("Roll 999", "Roll 1023")
    self.pvWidgetList.append(roll99)
    layout.addWidget(roll99, rowIdx + 1, colIdx-1, 1, 1)

    #*-------------------------- Add Group for RAM
    rowIdx = 0
    colIdx = 4
    groupBox_auxIO = QGroupBox("Wheel RAM Controls")
    ram_layout = QGridLayout()
    ram_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_auxIO.setLayout(ram_layout)
    layout.addWidget(groupBox_auxIO, rowIdx, colIdx, 10, 1)

    row = 0
    col = 0
    ram_layout.addWidget(GLabel("Wheel Map"), row, col)

    ram_pv = ["VETO_RAM", "TRIG_RAM", "SWEEP_RAM"]
    not_ram_pv = ["VETO_RAM_ADDR_SRC", "TRIG_RAM_ADDR_SRC", "SWEEP_RAM_ADDR_SRC"]

    self.ram_pvList = [[] for _ in ram_pv]
    self.ram_window = [[] for _ in range(len(ram_pv))]

    for pv in self.board.Board_PV:
      if not isinstance(pv, PV):
        continue
      pvName = pv.name.split(":")[-1]

      if any(pvName.startswith(prefix) for prefix in ram_pv) and pvName not in not_ram_pv:
        for idx, prefix in enumerate(ram_pv):
          if pvName.startswith(prefix):
            self.ram_pvList[idx].append(pv)


    self.combo_ramSel = QComboBox()
    self.combo_ramSel.addItem("Select RAM")
    for i in range(len(ram_pv)):
      self.combo_ramSel.addItem(f"{ram_pv[i]}")
      self.ram_pvList[i].sort(key=lambda pv: natural_key(pv.name))
    self.combo_ramSel.setCurrentIndex(0)
    self.combo_ramSel.currentIndexChanged.connect(self.OnRamChanged)
    ram_layout.addWidget(self.combo_ramSel, row, col + 1)

    row = 1

    hline = QFrame()
    hline.setFrameShape(QFrame.Shape.HLine)
    # hline.setFrameShadow(QFrame.Shadow.Sunken)
    ram_layout.addWidget(hline, row, 0, 1, ram_layout.columnCount())
    row += 1

    ram_layout.addWidget(GLabel("Trig Src. Select", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 1, 1, 1)
    ramDisplay = ["VETO", "TRIG", "SWEEP"]

    row += 1
    for i in range(len(not_ram_pv)):
      ram_layout.addWidget(GLabel(f"{ramDisplay[i]}  "), row, col)
      ramSrc = RComboBox(self.FindPV(not_ram_pv[i]), parent=self)
      ram_layout.addWidget(ramSrc, row, col + 1)
      self.pvWidgetList.append(ramSrc)
      row += 1

    hline1 = QFrame()
    hline1.setFrameShape(QFrame.Shape.HLine)
    # hline.setFrameShadow(QFrame.Shadow.Sunken)
    ram_layout.addWidget(hline1, row, 0, 1, ram_layout.columnCount())
    row += 1

    ram_layout.addWidget(GLabel("Sweep Mux"), row, col)
    sweepMux = RComboBox(self.FindPV("SweepMux"), parent=self)
    ram_layout.addWidget(sweepMux, row, col + 1)
    self.pvWidgetList.append(sweepMux)

    row += 1
    ram_layout.addWidget(GLabel("Sweep Pulse Width"), row, col)
    sweepWidth = RLineEdit(self.FindPV("Sweep_pw"), parent=self)
    ram_layout.addWidget(sweepWidth, row, col + 1)
    self.pvWidgetList.append(sweepWidth)


  #&---------------------------------------------------------
  def onSerialOrParallelChanged(self, state):
    if state == False:
      self.ssiInput.setEnabled(True)
      self.ssiTransLen.setEnabled(True)
      self.polarity.setEnabled(False)
    else: 
      self.ssiInput.setEnabled(False)
      self.ssiTransLen.setEnabled(False)
      self.polarity.setEnabled(True)


  def OnRamChanged(self, index):
    if index == 0:
      return
    ram_name = f"{self.combo_ramSel.currentText()}"
    self.combo_ramSel.setCurrentIndex(0)

    ramIdx = index - 1
    # Show the RAM PVs in a new window
    if self.ram_window[ramIdx]:
      self.ram_window[ramIdx].show()
      self.ram_window[ramIdx].raise_()
      self.ram_window[ramIdx].activateWindow()
      return

    self.ram_window[ramIdx] = RAMWindow(ram_name, self.ram_pvList[ramIdx], self)
    self.ram_window[ramIdx].show()



#@========================================================================================
class linkControlTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board,parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)


    rowIdx = 0
    colIdx = 0


    #&================ Create a group box for Link Controls
    link_pv = [ "LOCK",  "DEN",  "REN",  "SYNC", "RPwr", "TPwr", "SLiL", "SLoL", "ILM" , "XLM", "YLM"]
    link_display = ["Locked", "Drv. En.", "Rec. En", "Sync", "Rx Pwr", "Tx Pwr", "Line Loopback", "Local loopback", "Input Link Mask", "X En.", "Y En."]
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
    layout.addWidget(groupBox_Link, rowIdx, colIdx, 10, 1 )

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


    # Create a group box for Loopback Registers inside groupBox_Link
    groupBox_loopback = QGroupBox("Loopback Registers / LVDS Pre-Emph")
    loopback_layout = QGridLayout()
    loopback_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_loopback.setLayout(loopback_layout)
    link_layout.addWidget(groupBox_loopback, subRowIndex, 0)

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


    #&================ Create LRU
    colIdx = 1
    groupBox_LRU = QGroupBox("LRU Controls")
    lru_layout = QGridLayout()
    lru_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_LRU.setLayout(lru_layout)
    layout.addWidget(groupBox_LRU, rowIdx, colIdx, 10, 1 )

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
    lru_layout.addWidget(GLabel("Link L Stringent"), row, 0)
    linkLStringent = RTwoStateButton(self.FindPV("LINK_L_STRINGENT"),  width=30, parent=self)
    lru_layout.addWidget(linkLStringent, row, 1)
    self.pvWidgetList.append(linkLStringent)

    row += 1
    lru_layout.addWidget(GLabel("Link R Stringent"), row, 0)
    linkRStringent = RTwoStateButton(self.FindPV("LINK_R_STRINGENT"), width=30, parent=self)
    lru_layout.addWidget(linkRStringent, row, 1)
    self.pvWidgetList.append(linkRStringent)

    row += 1
    lru_layout.addWidget(GLabel("Link U Stringent"), row, 0)
    linkUStringent = RTwoStateButton(self.FindPV("LINK_U_STRINGENT"), width=30, parent=self)
    lru_layout.addWidget(linkUStringent, row, 1)
    self.pvWidgetList.append(linkUStringent)  
                                     
    vline = QFrame()
    vline.setFrameShape(QFrame.Shape.VLine)
    lru_layout.addWidget(vline, 0, 2, layout.rowCount(), 1)

    #------------------ LRU 
    row = 0
    col = 3
    lru_layout.addWidget(GLabel("L", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 1)
    lru_layout.addWidget(GLabel("U", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 2)
    lru_layout.addWidget(GLabel("R", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 3)

    row += 1
    lru_layout.addWidget(GLabel("SM locked"), row, col)
    lsmLock = RTwoStateButton(self.FindPV("L_SM_LOCKED"), width=30, parent=self)
    lsmLock.ClearTxt()
    usmLock = RTwoStateButton(self.FindPV("U_SM_LOCKED"), width=30, parent=self)
    usmLock.ClearTxt()
    rsmLock = RTwoStateButton(self.FindPV("R_SM_LOCKED"), width=30, parent=self)
    rsmLock.ClearTxt()

    lru_layout.addWidget(lsmLock, row, col + 1)
    lru_layout.addWidget(usmLock, row, col + 2)
    lru_layout.addWidget(rsmLock, row, col + 3)
    
    self.pvWidgetList.append(lsmLock)
    self.pvWidgetList.append(usmLock)
    self.pvWidgetList.append(rsmLock)

    row += 1
    lru_layout.addWidget(GLabel("SM lost lock"), row, col)
    lsmLostLock = RTwoStateButton(self.FindPV("L_LOST_LOCK"), width=30, parent=self)
    lsmLostLock.ClearTxt()
    usmLostLock = RTwoStateButton(self.FindPV("U_LOST_LOCK"), width=30, parent=self)
    usmLostLock.ClearTxt()
    rsmLostLock = RTwoStateButton(self.FindPV("R_LOST_LOCK"), width=30, parent=self)
    rsmLostLock.ClearTxt()

    lru_layout.addWidget(lsmLostLock, row, col + 1)
    lru_layout.addWidget(usmLostLock, row, col + 2)
    lru_layout.addWidget(rsmLostLock, row, col + 3)

    self.pvWidgetList.append(lsmLostLock)
    self.pvWidgetList.append(usmLostLock)
    self.pvWidgetList.append(rsmLostLock)

    row += 1
    lru_layout.addWidget(GLabel("Reset Lost Lock"), row, col)
    lsmResetLostLock = RTwoStateButton(self.FindPV("LostLockRstL"), width=30, parent=self)
    lsmResetLostLock.ClearTxt()
    usmResetLostLock = RTwoStateButton(self.FindPV("LostLockRstU"), width=30, parent=self)
    usmResetLostLock.ClearTxt()
    rsmResetLostLock = RTwoStateButton(self.FindPV("LostLockRstR"), width=30, parent=self)
    rsmResetLostLock.ClearTxt()

    lru_layout.addWidget(lsmResetLostLock, row, col + 1)
    lru_layout.addWidget(usmResetLostLock, row, col + 2)
    lru_layout.addWidget(rsmResetLostLock, row, col + 3)  

    self.pvWidgetList.append(lsmResetLostLock)
    self.pvWidgetList.append(usmResetLostLock)
    self.pvWidgetList.append(rsmResetLostLock)

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
    lru_layout.addWidget(GLabel("Reset Rcv DCbal"), row, col, 1, 2)
    rsmRcvDCbal = RTwoStateButton(self.FindPV("RST_LINKR_DCBAL"), width=30, parent=self)
    rsmRcvDCbal.ClearTxt()
    usmRcvDCbal = RTwoStateButton(self.FindPV("RST_LINKU_DCBAL"), width=30, parent=self)
    usmRcvDCbal.ClearTxt()

    lru_layout.addWidget(usmRcvDCbal, row, col + 2)
    lru_layout.addWidget(rsmRcvDCbal, row, col + 3)

    self.pvWidgetList.append(usmRcvDCbal)
    self.pvWidgetList.append(rsmRcvDCbal)

#@========================================================================================
class CPLDControlTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board,parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    #&================ Create a group box for Remote Master Logic L
    groupBox_remoteMaster = QGroupBox("Remote Master Logic")
    remoteMaster_layout = QGridLayout()
    remoteMaster_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_remoteMaster.setLayout(remoteMaster_layout)
    layout.addWidget(groupBox_remoteMaster, 0, 0, 1, 1)

    row = 0
    remoteMaster_layout.addWidget(GLabel("L", alignment=Qt.AlignmentFlag.AlignHCenter), row, 1)
    remoteMaster_layout.addWidget(GLabel("R", alignment=Qt.AlignmentFlag.AlignHCenter), row, 2)
    remoteMaster_layout.addWidget(GLabel("U", alignment=Qt.AlignmentFlag.AlignHCenter), row, 3)

    row += 1
    remoteMaster_layout.addWidget(GLabel("Remote TS offset"), row, 0)

    self.remoteTSoffsetL = RLineEdit(self.FindPV("reg_REMOTE_TRIGGER_TS_OFFSET_L"), parent=self)
    self.remoteTSoffsetR = RLineEdit(self.FindPV("reg_REMOTE_TRIGGER_TS_OFFSET_R"), parent=self)
    self.remoteTSoffsetU = RLineEdit(self.FindPV("reg_REMOTE_TRIGGER_TS_OFFSET_U"), parent=self)
    remoteMaster_layout.addWidget(self.remoteTSoffsetL, row, 1)
    remoteMaster_layout.addWidget(self.remoteTSoffsetR, row, 2)
    remoteMaster_layout.addWidget(self.remoteTSoffsetU, row, 3)
    self.pvWidgetList.append(self.remoteTSoffsetL)
    self.pvWidgetList.append(self.remoteTSoffsetR)
    self.pvWidgetList.append(self.remoteTSoffsetU)

    row += 1
    remoteMaster_layout.addWidget(GLabel("Remote Dig offset"), row, 0)
    self.remoteDigTSoffsetL = RLineEdit(self.FindPV("reg_REMOTE_TRIG_DIG_OFFSET_L"), parent=self)
    self.remoteDigTSoffsetR = RLineEdit(self.FindPV("reg_REMOTE_TRIG_DIG_OFFSET_R"), parent=self)
    self.remoteDigTSoffsetU = RLineEdit(self.FindPV("reg_REMOTE_TRIG_DIG_OFFSET_U"), parent=self)
    remoteMaster_layout.addWidget(self.remoteDigTSoffsetL, row, 1)
    remoteMaster_layout.addWidget(self.remoteDigTSoffsetR, row, 2)
    remoteMaster_layout.addWidget(self.remoteDigTSoffsetU, row, 3)
    self.pvWidgetList.append(self.remoteDigTSoffsetL)
    self.pvWidgetList.append(self.remoteDigTSoffsetR)
    self.pvWidgetList.append(self.remoteDigTSoffsetU)

    row += 1
    remoteMaster_layout.addWidget(GLabel("Local Coinc. Mask"), row, 0)
    self.remoteCoincMaskL = RLineEdit(self.FindPV("L_COINC_MASK"), hexBinDec="bin", parent=self)
    self.remoteCoincMaskR = RLineEdit(self.FindPV("R_COINC_MASK"), hexBinDec="bin", parent=self)
    self.remoteCoincMaskU = RLineEdit(self.FindPV("U_COINC_MASK"), hexBinDec="bin", parent=self)
    remoteMaster_layout.addWidget(self.remoteCoincMaskL, row, 1)
    remoteMaster_layout.addWidget(self.remoteCoincMaskR, row, 2)
    remoteMaster_layout.addWidget(self.remoteCoincMaskU, row, 3)
    self.pvWidgetList.append(self.remoteCoincMaskL)
    self.pvWidgetList.append(self.remoteCoincMaskR)
    self.pvWidgetList.append(self.remoteCoincMaskU)

    row += 1
    remoteMaster_layout.addWidget(GLabel("Local Trig Delay"), row, 0)
    self.localTrigDelayL = RLineEdit(self.FindPV("reg_LOCAL_TRIG_DELAY_L"), parent=self)
    self.localTrigDelayR = RLineEdit(self.FindPV("reg_LOCAL_TRIG_DELAY_R"), parent=self)
    self.localTrigDelayU = RLineEdit(self.FindPV("reg_LOCAL_TRIG_DELAY_U"), parent=self)
    remoteMaster_layout.addWidget(self.localTrigDelayL, row, 1)
    remoteMaster_layout.addWidget(self.localTrigDelayR, row, 2)
    remoteMaster_layout.addWidget(self.localTrigDelayU, row, 3)
    self.pvWidgetList.append(self.localTrigDelayL)
    self.pvWidgetList.append(self.localTrigDelayR)
    self.pvWidgetList.append(self.localTrigDelayU)

    row += 1
    remoteMaster_layout.addWidget(GLabel("Overlap Time"), row, 0)
    self.remoteOverlapTimeL = RLineEdit(self.FindPV("L_OVERLAP_DELAY"), parent=self)
    self.remoteOverlapTimeR = RLineEdit(self.FindPV("R_OVERLAP_DELAY"), parent=self)
    self.remoteOverlapTimeU = RLineEdit(self.FindPV("U_OVERLAP_DELAY"), parent=self)
    remoteMaster_layout.addWidget(self.remoteOverlapTimeL, row, 1)
    remoteMaster_layout.addWidget(self.remoteOverlapTimeR, row, 2)
    remoteMaster_layout.addWidget(self.remoteOverlapTimeU, row, 3)
    self.pvWidgetList.append(self.remoteOverlapTimeL)
    self.pvWidgetList.append(self.remoteOverlapTimeR)
    self.pvWidgetList.append(self.remoteOverlapTimeU)

    row += 1
    remoteMaster_layout.addWidget(GLabel("Remote Trig Delay"), row, 0)
    self.remoteTrigDelayL = RLineEdit(self.FindPV("reg_REMOTE_TRIG_DELAY_L"), parent=self)
    self.remoteTrigDelayR = RLineEdit(self.FindPV("reg_REMOTE_TRIG_DELAY_R"), parent=self)
    self.remoteTrigDelayU = RLineEdit(self.FindPV("reg_REMOTE_TRIG_DELAY_U"), parent=self)
    remoteMaster_layout.addWidget(self.remoteTrigDelayL, row, 1)
    remoteMaster_layout.addWidget(self.remoteTrigDelayR, row, 2)
    remoteMaster_layout.addWidget(self.remoteTrigDelayU, row, 3)
    self.pvWidgetList.append(self.remoteTrigDelayL)
    self.pvWidgetList.append(self.remoteTrigDelayR)
    self.pvWidgetList.append(self.remoteTrigDelayU)

    row += 1
    self.remoteModeL = RTwoStateButton(self.FindPV("L_RT_TS_MODE"), parent=self)
    self.remoteModeR = RTwoStateButton(self.FindPV("R_RT_TS_MODE"), parent=self)
    self.remoteModeU = RTwoStateButton(self.FindPV("U_RT_TS_MODE"), parent=self)

    self.remoteModeL.SetTexts("Message\nTS Mode", "Delay\nLine Mode")
    self.remoteModeR.SetTexts("Message\nTS Mode", "Delay\nLine Mode")
    self.remoteModeU.SetTexts("Message\nTS Mode", "Delay\nLine Mode")

    self.remoteModeL.stateChanged.connect(lambda state, LRU="L": self.WhenRMLModeChanged(state, LRU))
    self.remoteModeR.stateChanged.connect(lambda state, LRU="R": self.WhenRMLModeChanged(state, LRU))
    self.remoteModeU.stateChanged.connect(lambda state, LRU="U": self.WhenRMLModeChanged(state, LRU))

    remoteMaster_layout.addWidget(self.remoteModeL, row, 1)
    remoteMaster_layout.addWidget(self.remoteModeR, row, 2)
    remoteMaster_layout.addWidget(self.remoteModeU, row, 3)
    self.pvWidgetList.append(self.remoteModeL)
    self.pvWidgetList.append(self.remoteModeR)
    self.pvWidgetList.append(self.remoteModeU)

    row += 1
    txt = "Explanation for the Message TS Mode:\nThe Remote TS/Dig offset is coincident with Local Coinc. Mask (that can be delayed)\nThe coincdient is controlled by the Overlap Time."

    remoteMaster_layout.addWidget(GLabel(txt, alignment=Qt.AlignmentFlag.AlignLeft), row, 0, 1, 4)


    
    #&================ Create a group box for CPLD control
    groupBox_CPLD = QGroupBox("CPLD Control")
    cpld_layout = QGridLayout()
    cpld_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_CPLD.setLayout(cpld_layout)
    layout.addWidget(groupBox_CPLD, 0, 1, 1, 1)

    row = 0
    cpld_layout.addWidget(GLabel("bit"), row, 1)
    cpld_layout.addWidget(GLabel("Sum"), row, 2)

    row += 1
    cpld_layout.addWidget(GLabel("A"), row, 0)
    cpldBitA = RLineEdit(self.FindPV("masked_bit_a"), parent=self)
    cpldSumA = RLineEdit(self.FindPV("masked_sum_a"), parent=self)
    cpld_layout.addWidget(cpldBitA, row, 1)
    cpld_layout.addWidget(cpldSumA, row, 2)
    self.pvWidgetList.append(cpldBitA)
    self.pvWidgetList.append(cpldSumA)

    row += 1
    cpld_layout.addWidget(GLabel("B"), row, 0)
    cpldBitB = RLineEdit(self.FindPV("masked_bit_b"), parent=self)
    cpldSumB = RLineEdit(self.FindPV("masked_sum_b"), parent=self)
    cpld_layout.addWidget(cpldBitB, row, 1)
    cpld_layout.addWidget(cpldSumB, row, 2) 
    self.pvWidgetList.append(cpldBitB)
    self.pvWidgetList.append(cpldSumB)

    row += 1
    cpld_layout.addWidget(GLabel("C"), row, 0)
    cpldBitC = RLineEdit(self.FindPV("masked_bit_c"), parent=self)
    cpldSumC = RLineEdit(self.FindPV("masked_sum_c"), parent=self)
    cpld_layout.addWidget(cpldBitC, row, 1)
    cpld_layout.addWidget(cpldSumC, row, 2)
    self.pvWidgetList.append(cpldBitC)
    self.pvWidgetList.append(cpldSumC)

    row += 1
    cpld_layout.addWidget(GLabel("D"), row, 0)
    cpldBitD = RLineEdit(self.FindPV("masked_bit_d"), parent=self)
    cpldSumD = RLineEdit(self.FindPV("masked_sum_d"), parent=self)
    cpld_layout.addWidget(cpldBitD, row, 1)
    cpld_layout.addWidget(cpldSumD, row, 2)
    self.pvWidgetList.append(cpldBitD)
    self.pvWidgetList.append(cpldSumD)

    row += 1
    cpld_layout.addWidget(GLabel("Mask reg"), row, 0, 1, 2)
    cpldMaskReg = RLineEdit(self.FindPV("reg_CPLD_MASK"), parent=self)
    cpld_layout.addWidget(cpldMaskReg, row, 2)
    self.pvWidgetList.append(cpldMaskReg)

    row += 1
    cpld_layout.addWidget(GLabel("Threshold (Hex)"), row, 0, 1, 2)
    cpldThreshold = RLineEdit(self.FindPV("reg_FS_MULT_THRESH"), hexBinDec="hex", parent=self)
    cpld_layout.addWidget(cpldThreshold, row, 2)
    self.pvWidgetList.append(cpldThreshold)

    row += 1
    cpld_layout.addWidget(GLabel("Multiplicity"), row, 0, 1, 2)
    cpldMultiplicity = RLineEdit(self.FindPV("reg_CPLD_MULT"), parent=self)
    cpld_layout.addWidget(cpldMultiplicity, row, 2)
    self.pvWidgetList.append(cpldMultiplicity)

    row += 1
    cpldMode = RComboBox(self.FindPV("FS_SEL"), parent=self)
    cpld_layout.addWidget(cpldMode, row, 1, 1, 2)
    self.pvWidgetList.append(cpldMode)


  def WhenRMLModeChanged(self, state, LRU):
    if LRU == "L" :
      self.remoteTSoffsetL.setEnabled(not state)
      self.remoteDigTSoffsetL.setEnabled(not state)
      self.remoteOverlapTimeL.setEnabled(not state)
      self.remoteCoincMaskL.setEnabled(not state)
      self.localTrigDelayL.setEnabled(not state)
      self.remoteTrigDelayL.setEnabled(state)

    elif LRU == "R" :
      self.remoteTSoffsetR.setEnabled(not state)
      self.remoteDigTSoffsetR.setEnabled(not state)
      self.remoteOverlapTimeR.setEnabled(not state)
      self.remoteCoincMaskR.setEnabled(not state)
      self.localTrigDelayR.setEnabled(not state)
      self.remoteTrigDelayR.setEnabled(state)

    elif LRU == "U" :
      self.remoteTSoffsetU.setEnabled(not state)
      self.remoteDigTSoffsetU.setEnabled(not state)
      self.remoteOverlapTimeU.setEnabled(not state)
      self.remoteCoincMaskU.setEnabled(not state)
      self.localTrigDelayU.setEnabled(not state)
      self.remoteTrigDelayU.setEnabled(state)

    
#@========================================================================================
class otherControlTab(templateTab):
  def __init__(self, board : Board, parent=None):
    super().__init__(board, parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    #&================ Create a group box for NIM Output Controls
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

    #&================ Create a group box for Trigger Data Readout
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

    trigData_layout.addWidget(GLabel("E", alignment=Qt.AlignmentFlag.AlignHCenter), row, 3)
    trigData_layout.addWidget(GLabel("AE", alignment=Qt.AlignmentFlag.AlignHCenter), row, 4)
    trigData_layout.addWidget(GLabel("AF", alignment=Qt.AlignmentFlag.AlignHCenter), row, 5)
    trigData_layout.addWidget(GLabel("F", alignment=Qt.AlignmentFlag.AlignHCenter), row, 6)

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
    trigData_layout.addWidget(GLabel("En. FIFO Mon  "), row, 0)
    fifoMonEna = RTwoStateButton(self.FindPV("SYSMON_ENABLE"), parent=self)
    trigData_layout.addWidget(fifoMonEna, row, 1)
    self.pvWidgetList.append(fifoMonEna)

    resetFifo = RTwoStateButton(self.FindPV("reg_FIFO_RESETS"), parent=self)
    resetFifo.SetTexts("Normal", "Reset FFIO")
    resetFifo.SetInvertStateColor(True)
    trigData_layout.addWidget(resetFifo, row, 2)
    self.pvWidgetList.append(resetFifo)

    fifoCount = RLineEdit(self.FindPV("reg_MON7_FIFO_DEPTH"), parent=self)
    fifoCount.setFixedWidth(100)
    trigData_layout.addWidget(fifoCount, row, 3, 1, 4)
    self.pvWidgetList.append(fifoCount)


    #&================ Create a group box for LED Controls
    groupBox_ledControl = QGroupBox("LED Controls")
    led_layout = QGridLayout()
    led_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_ledControl.setLayout(led_layout)
    layout.addWidget(groupBox_ledControl, 0, 5, 2, 1)

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




#^###########################################################################################################
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
    self.miscState = RRegisterDisplay(self.FindPV("reg_MISC_STAT"), False, parent=self)
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

    info_layout.addWidget(GLabel("Imp Sync  ", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    impSync = RTwoStateButton( self.FindPV("IMP_SYNC"), parent=self)
    info_layout.addWidget(impSync, row, col + 1)
    self.pvWidgetList.append(impSync)
    row += 1

    info_layout.addWidget(GLabel("Read Out", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    readout = RTwoStateButton( self.FindPV("CS_Ena"), parent=self)
    info_layout.addWidget(readout, row, col + 1)
    self.pvWidgetList.append(readout)
    row += 1

    fifoToRead = RComboBox( self.FindPV("FifoNum"), parent=self)
    info_layout.addWidget(fifoToRead, row, col, 1, 2)
    self.pvWidgetList.append(fifoToRead)
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
      highWidget = RLineEdit(highPV, width=80, parent=self)
      lowWidget = RLineEdit(lowPV, width=80, parent=self)
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
      highWidget = RLineEdit(highPV,width=80, parent=self)
      lowWidget = RLineEdit(lowPV, width=80, parent=self)
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
      pvWidget = RLineEdit(pv, width = 80, parent=self)
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
    self.tab2 = wheelRAMTab(self.board, parent=self)
    self.tab3 = linkControlTab(self.board, parent=self)
    self.tab4 = CPLDControlTab(self.board, parent=self)
    self.tab5 = otherControlTab(self.board, parent=self)

    self.tabs.addTab(self.tab1, "Trigger/Veto Control")
    self.tabs.addTab(self.tab2, "Wheel RAM")
    self.tabs.addTab(self.tab3, "LINK Control")
    self.tabs.addTab(self.tab4, "Trigger/CPLD map")
    self.tabs.addTab(self.tab5, "Other Control")

    self.tabs.setCurrentWidget(self.tab5)

    # Connect tab change to force PV update
    self.tabs.currentChanged.connect(lambda idx: self.tabs.widget(idx).UpdatePVs(True)) #force the pv.isUpdate to be False, so that the pv will be displayed.


    #------------------------------ QTimer for updating PVs
    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second


    # #------------------- find all PV not used
    # allUsedPV = set()
    # allUsedPV.add(self.miscState.pv)

    # for pvWidget in self.pvWidgetList:
    #   if not isinstance(pvWidget, RMapTwoStateButton): 
    #     allUsedPV.add(pvWidget.pv)
    #   elif isinstance(pvWidget, RMapTwoStateButton):
    #     for button in pvWidget.buttons:
    #       for row in pvWidget.buttons:
    #         for button in row:
    #           allUsedPV.add(button.pv)

    # for i, tab in enumerate([self.tab1, self.tab2, self.tab3, self.tab4, self.tab5]):
    #   print(f"=========================== Tab {i}: {tab.__class__.__name__}")
    #   for pvWidget in tab.pvWidgetList:
    #     if not isinstance(pvWidget, RMapTwoStateButton): 
    #       allUsedPV.add(pvWidget.pv)
    #     elif isinstance(pvWidget, RMapTwoStateButton):
    #       for row in pvWidget.buttons:
    #         for button in row:
    #           allUsedPV.add(button.pv)

    # unusedPV = [pv for pv in self.board.Board_PV if pv not in allUsedPV]
    # unusedPV = [pv for pv in unusedPV if not any(pv.name.split(":")[-1].startswith(prefix) for prefix in ["VETO_RAM", "TRIG_RAM", "SWEEP_RAM"])]

    # print(f"=========================== Unused PVs: {len(unusedPV)}")
    # for pv in unusedPV:
    #   print(f"{pv}")


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

    # Only update the tab that is currently active
    current_tab = self.tabs.currentWidget()
    if current_tab is self.tab1:
      self.tab1.UpdatePVs()
    elif current_tab is self.tab2:
      self.tab2.UpdatePVs()
    elif current_tab is self.tab3:
      self.tab3.UpdatePVs()
    elif current_tab is self.tab4:
      self.tab4.UpdatePVs()
    elif current_tab is self.tab5:
      self.tab5.UpdatePVs()
