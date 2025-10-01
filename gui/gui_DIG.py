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



#^###########################################################################################################
class DIGWindow(QMainWindow):
  def __init__(self, board_name, board : Board):
    super().__init__()

    self.board = board

    self.setWindowTitle(board_name)
    self.setGeometry(150, 150, 600, 600)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #================================ PV Widgets
    self.pvWidgetList = []

    rowIdx = 0
    colIdx = 0

    #&================================ Board Info
    pvNameList = [
      ["regin_code_revision", "Code Revision", True],
      ["code_date", "Code Date", True],
      ["vme_code_revision", "VME Code Rev.", True],
      ["serial_num", "Serial No.", True],
      ["live_timestamp_msb", "Timestamp MSB", True],
      ["live_timestamp_lsb", "Timestamp LSB", True],  
      ["geo_addr", "Geo Addr", False],
      ["user_package_data", "Board ID", False],
      ["fw_type", "FW Type", False],
      ["reg_led_state", "LED State", True]
    ]

    groupBox_info = QGroupBox("Board Info / Status")
    info_layout = QGridLayout()
    info_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_info.setLayout(info_layout)
    layout.addWidget(groupBox_info, rowIdx, colIdx, 1, 2)
    
    row = 0
    col = 0

    for pvName, displayName, isHex in pvNameList:
      pv = self.FindPV(pvName)
      if pv is not None:
        info_layout.addWidget(GLabel(displayName, alignment=Qt.AlignmentFlag.AlignRight), row, col)
        if isHex:
          pvWidget = RLineEdit(pv, hexBinDec="hex", width= 120, parent=self)
        else: 
          pvWidget = RLineEdit(pv, width= 120, parent=self)
        info_layout.addWidget(pvWidget, row, col + 1)
        self.pvWidgetList.append(pvWidget)
        row += 1


    #.......... TwoStateButton
    row = 0
    col = 3

    info_layout.addWidget(GLabel("Power OK", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    powerOk = RTwoStateButton(self.FindPV("power_ok"), parent=self)
    info_layout.addWidget(powerOk, row, col + 1)
    self.pvWidgetList.append(powerOk)
    row += 1

    info_layout.addWidget(GLabel("Over Volt Stat", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    overVoltStat = RTwoStateButton(self.FindPV("over_volt_stat"), parent=self)
    info_layout.addWidget(overVoltStat, row, col + 1)
    self.pvWidgetList.append(overVoltStat)

    row += 1
    info_layout.addWidget(GLabel("Under Volt Stat", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    underVoltStat = RTwoStateButton(self.FindPV("under_volt_stat"), parent=self)
    info_layout.addWidget(underVoltStat, row, col + 1)
    self.pvWidgetList.append(underVoltStat)

    row += 1
    info_layout.addWidget(GLabel("Temp Sensor 0", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    tempSensor0 = RTwoStateButton(self.FindPV("temp0_sensor"), parent=self)
    info_layout.addWidget(tempSensor0, row, col + 1)
    self.pvWidgetList.append(tempSensor0)

    row += 1
    info_layout.addWidget(GLabel("Temp Sensor 1", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    tempSensor1 = RTwoStateButton(self.FindPV("temp1_sensor"), parent=self)
    info_layout.addWidget(tempSensor1, row, col + 1)
    self.pvWidgetList.append(tempSensor1)

    row += 1
    info_layout.addWidget(GLabel("Temp Sensor 2", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    tempSensor2 = RTwoStateButton(self.FindPV("temp2_sensor"), parent=self)
    info_layout.addWidget(tempSensor2, row, col + 1)
    self.pvWidgetList.append(tempSensor2)




    #&================================ Channel Triggers/Controls
    rowIdx += 1
    colIdx = 0

    groupBox_chTrig = QGroupBox("Channel Triggers/Controls")
    chTrig_layout = QGridLayout()
    chTrig_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_chTrig.setLayout(chTrig_layout)
    layout.addWidget(groupBox_chTrig, rowIdx, colIdx, 1, 1)

    row = 0
    col = 0

    chTrig_layout.addWidget(GLabel("Threshold", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 1)
    chTrig_layout.addWidget(GLabel("Trigger", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 2)
    chTrig_layout.addWidget(GLabel("Accepted", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 3)
    chTrig_layout.addWidget(GLabel("Dn. Samp.", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 4)

    for i in range(10):
      row += 1
      chTrig_layout.addWidget(GLabel(f"{i}", alignment=Qt.AlignmentFlag.AlignRight), row, col)
      pv = self.FindChannelPV(i, "channel_enable")
      if pv is not None:
        chEnable = RTwoStateButton(pv, width= 60, parent=self)
        chEnable.SetTexts("Off", "On")
        chTrig_layout.addWidget(chEnable, row, col + 0)
        self.pvWidgetList.append(chEnable)

      pv = self.FindChannelPV(i, "led_threshold")
      if pv is not None:
        chThreshold = RLineEdit(pv, width=65, parent=self)
        chTrig_layout.addWidget(chThreshold, row, col + 1)
        self.pvWidgetList.append(chThreshold)

      pv = self.FindChannelPV(i, "disc_count")
      if pv is not None:
        chTrigger = RLineEdit(pv, width=80, parent=self)
        chTrig_layout.addWidget(chTrigger, row, col + 2)
        self.pvWidgetList.append(chTrigger)

      pv = self.FindChannelPV(i, "ahit_count")
      if pv is not None:
        chAccepted = RLineEdit(pv, width=80, parent=self)
        chTrig_layout.addWidget(chAccepted, row, col + 3)
        self.pvWidgetList.append(chAccepted)

      pv = self.FindChannelPV(i, "downsample_factor")
      if pv is not None:
        chDownSample = RComboBox(pv, width=80, parent=self)
        chTrig_layout.addWidget(chDownSample, row, col + 4)
        self.pvWidgetList.append(chDownSample)

    #&================================ Throttle Control
    rowIdx = 2
    colIdx = 0

    groupBox_throttle = QGroupBox("Throttle Control")
    throttle_layout = QGridLayout()
    throttle_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_throttle.setLayout(throttle_layout)
    layout.addWidget(groupBox_throttle, rowIdx, colIdx, 1, 1)

    row = 0
    col = 0
    throttle_layout.addWidget(GLabel("Throttle Mode", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    throttleMode = RComboBox(self.FindPV("rj45_throttle_mode"), width = 80, parent=self)
    throttle_layout.addWidget(throttleMode, row, col + 1)
    self.pvWidgetList.append(throttleMode)

    col += 2
    throttle_layout.addWidget(GLabel("LFSR rate", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    ifsrRate = RComboBox(self.FindPV("lfsr_rate_sel"), width=80, parent=self)
    throttle_layout.addWidget(ifsrRate, row, col + 1)
    self.pvWidgetList.append(ifsrRate)

    row += 1
    col = 0
    throttle_layout.addWidget(GLabel("Prog. Throttle Mode", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    progThrottleMode = RComboBox(self.FindPV("FIFO_Prog_Thresh"), width = 80, parent=self)
    throttle_layout.addWidget(progThrottleMode, row, col + 1)
    self.pvWidgetList.append(progThrottleMode)

    col += 2
    throttle_layout.addWidget(GLabel("LFSR seed", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    ifsrSeed = RLineEdit(self.FindPV("lfsr_seed"), width=80, parent=self)
    throttle_layout.addWidget(ifsrSeed, row, col + 1)
    self.pvWidgetList.append(ifsrSeed)


    #&================================ Board Control
    rowIdx = 1
    colIdx = 1

    groupBox_control = QGroupBox("Board Control")
    control_layout = QGridLayout()
    control_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_control.setLayout(control_layout)
    layout.addWidget(groupBox_control, rowIdx, colIdx, 2, 1)

    row = 0
    col = 0

    control_layout.addWidget(GLabel("Master Logic", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    masterLogic = RTwoStateButton(self.FindPV("master_logic_enable"), parent=self)
    control_layout.addWidget(masterLogic, row, col + 1)
    self.pvWidgetList.append(masterLogic)

    row += 1
    control_layout.addWidget(GLabel("Readout", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    readout = RTwoStateButton(self.FindPV("CS_Ena"), parent=self)
    control_layout.addWidget(readout, row, col + 1)
    self.pvWidgetList.append(readout)

    row += 1
    control_layout.addWidget(GLabel("Trig Mode", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    trigMode = RComboBox(self.FindPV("trigger_mux_select"), parent=self)
    control_layout.addWidget(trigMode, row, col + 1)
    self.pvWidgetList.append(trigMode)

    row += 1
    control_layout.addWidget(GLabel("CFD Mode", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    cfdMode = RComboBox(self.FindPV("cfd_mode"), parent=self)
    control_layout.addWidget(cfdMode, row, col + 1)
    self.pvWidgetList.append(cfdMode)
    
    row += 1
    control_layout.addWidget(GLabel("Comp. Win Min [us]", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    compWinMin = RLineEdit(self.FindPV("win_comp_min"), width=120, parent=self)
    control_layout.addWidget(compWinMin, row, col + 1)
    self.pvWidgetList.append(compWinMin)

    row += 1
    control_layout.addWidget(GLabel("Comp. Win Max [us]", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    compWinMax = RLineEdit(self.FindPV("win_comp_max"), width=120, parent=self)
    control_layout.addWidget(compWinMax, row, col + 1)
    self.pvWidgetList.append(compWinMax)



    row += 1
    control_layout.addWidget(GLabel("Master FIFO Reset", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    mstrFifoRst = RTwoStateButton(self.FindPV("master_fifo_reset"), parent=self)
    control_layout.addWidget(mstrFifoRst, row, col + 1)
    self.pvWidgetList.append(mstrFifoRst)

    row += 1
    control_layout.addWidget(GLabel("Veto", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    veto = RTwoStateButton(self.FindPV("veto_enable"), parent=self)
    control_layout.addWidget(veto, row, col + 1)
    self.pvWidgetList.append(veto)

    row += 1
    control_layout.addWidget(GLabel("Clock Scr", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    clkScr = RTwoStateButton(self.FindPV("clk_select"), parent=self)
    control_layout.addWidget(clkScr, row, col + 1)
    self.pvWidgetList.append(clkScr)

    row += 1
    control_layout.addWidget(GLabel("Reset Lost Lock", alignment=Qt.AlignmentFlag.AlignRight), row, col)
    rstLostLock = RTwoStateButton(self.FindPV("sd_sm_lost_lock_flag_rst"), parent=self)
    control_layout.addWidget(rstLostLock, row, col + 1  )

    row += 1
    control_layout.addWidget(GLabel("Ext Disc. TS", alignment=Qt.AlignmentFlag.AlignRight), row , col)
    extDiscTs = RComboBox(self.FindPV("ext_disc_ts_sel"), parent=self)
    control_layout.addWidget(extDiscTs, row, col + 1)
    self.pvWidgetList.append(extDiscTs)

    #================================ QTimer for updating PVs
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
  
  def FindChannelPV(self, channel : int, pv_name) -> PV:
    for pv in self.board.CH_PV[channel]:
      pvName = pv.name.split(":")[-1]
      if pvName.startswith(pv_name):
        return pv
    return None

  def UpdatePVs(self):
    # if not self.isActiveWindow() or not self.isVisible():
    #   return

    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV()

    # current_tab = self.tabs.currentWidget()
    # if current_tab is self.tab1:
    #   self.tab1.UpdatePVs()
    # elif current_tab is self.tab2:
    #   self.tab2.UpdatePVs()
