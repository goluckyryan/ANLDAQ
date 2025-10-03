from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget, QGroupBox, QPushButton, QFrame, QComboBox, QLabel
from PyQt6.QtCore import Qt, QTimer

from class_Board import Board
from class_PV import PV
from custom_QClasses import GLabel, GLineEdit
from class_PVWidgets import RRegisterDisplay, RLineEdit, RTwoStateButton, RComboBox, RMapTwoStateButton, RSetButton, RMapLineEdit
from gui_RAM import RAMWindow
import re

from aux import make_pattern_list, natural_key

from gui_MTRG import templateTab

from gui_CH import CHWindow

#^###########################################################################################################
class DIGWindow(QMainWindow):
  def __init__(self, board_name, board : Board):
    super().__init__()

    self.board = board
    self.isACQRunning = False

    self.setWindowTitle(board_name)
    self.setGeometry(150, 150, 600, 600)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    self.chWindows = None

    #================================ PV Widgets
    self.pvWidgetList = []

    #&================================ Board Info
    pvNameList = [
      ["regin_code_revision",            "Code Revision",     True  ],
      ["code_date",                      "Code Date",         True  ],
      ["vme_code_revision",              "VME Code Rev.",     True  ],
      ["serial_num",                     "Serial No.",        True  ],
      ["live_timestamp_msb",             "Timestamp MSB",     True  ],
      ["live_timestamp_lsb",             "Timestamp LSB",     True  ],  
      ["geo_addr",                       "Geo Addr",          False ],
      ["user_package_data",              "Board ID",          False ],
      ["fw_type",                        "FW Type",           False ],
      ["reg_led_state",                  "LED State",         True  ], 
      ["power_ok",                       "Power OK",          False ],
      ["over_volt_stat",                 "Over Volt Stat",    False ],
      ["under_volt_stat",                "Under Volt Stat",   False ],
      ["temp0_sensor",                   "Temp Sensor 0",     False ],
      ["temp1_sensor",                   "Temp Sensor 1",     False ],
      ["temp2_sensor",                   "Temp Sensor 2",     False ],
      ["reg_master_logic_status",        "Misc. Log. Status", True  ],
      ["reg_sd_config",                  "SD Config",         True  ],
      ["vme_gp_ctrl",                    "VME gp Ctrl",       True  ],
      ["reg_external_discriminator_src", "Ext. Disc. Src",    True  ],
      ["reg_external_disc_mode",         "Ext. Disc. Mode",   True  ],
      ["regin_ts_err_count",             "TS Err Count",      True  ]
    ]

    groupBox_info = QGroupBox("Board Info / Status")
    info_layout = QGridLayout()
    info_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_info.setLayout(info_layout)
    
    self.FillWidgets(info_layout, pvNameList, maxRows = 11, widgetWidth = 90)

    #&================================ Serders Status/Control
    pvNameList = [
      ["serdes_lock",                    "SerDes Lock",       False ],
      ["serdes_sm_locked",               "SM Locked",         False ],
      ["serdes_sm_lost_lock_flag",       "Lost Lock Flag",    False ],
      ["sd_rx_pwr",                      "Rx Pwr",            False ],
      ["sd_tx_pwr",                      "Tx Pwr",            False ],
      ["sd_local_loopback_en",           "Local Loopback",    False ],
      ["sd_line_loopback_en",            "Line Loopback",     False ],
      ["sd_pem",                         "PEM",               False ],
      ["sd_sync",                        "Sync",              False ],
      ["sd_sm_stringent_lock",           "Strngnt Lock",      False ]
    ]

    groupBox_serdes = QGroupBox("SerDes Status/Control")
    serdes_layout = QGridLayout()
    serdes_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
    groupBox_serdes.setLayout(serdes_layout)

    self.FillWidgets(serdes_layout, pvNameList, maxRows = 10, widgetWidth = 90)


    #&================================ FIFO Status/Control
    pvNameList = [
      ["master_fifo_reset",              "Master FIFO Reset", False ],
      ["fifo_a_empty",                   "FIFO A Empty",      False ],
      ["fifo_b_empty",                   "FIFO B Empty",      False ],
      ["fifo_a_full",                    "FIFO A Full",       False ],
      ["fifo_b_full",                    "FIFO B Full",       False ],
      ["fifo_fulla",                     "FIFO Full A",       False ],
      ["fifo_fullb",                     "FIFO Full B",       False ],
      ["fifo_almost_full",               "FIFO Almost Full",  False ],
      ["ini_fifo_prog_flag",             "FIFO Prog. Flag",   False ],
      ["fifo_depth",                     "FIFO Depth",        True  ],
      ["int_FIFO_PROG_ERR",              "FIFO Prog. Err",    False ],
      ["int_FIFO_PROG_FLG",              "FIFO Prog. Flg",    False ]
    ]

    groupBox_fifo = QGroupBox("FIFO Status/Control")
    fifo_layout = QGridLayout()
    fifo_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_fifo.setLayout(fifo_layout)

    self.FillWidgets(fifo_layout, pvNameList, maxRows = 9, widgetWidth = 90)

    #&================================ Channel Triggers/Controls
    groupBox_chTrig = QGroupBox("Channel Triggers/Controls")
    chTrig_layout = QGridLayout()
    chTrig_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_chTrig.setLayout(chTrig_layout)

    row = 0
    col = 0

    chTrig_layout.addWidget(GLabel("Threshold", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 2)
    chTrig_layout.addWidget(GLabel("Trigger", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 3)
    chTrig_layout.addWidget(GLabel("Accepted", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 4)
    chTrig_layout.addWidget(GLabel("Dn. Samp.", alignment=Qt.AlignmentFlag.AlignHCenter), row, col + 5)

    for i in range(10):
      row += 1
      chTrig_layout.addWidget(GLabel(f"{i}"), row, col)
      pv = self.FindChannelPV(i, "channel_enable")
      if pv is not None:
        chEnable = RTwoStateButton(pv, width= 70, parent=self)
        chEnable.SetTexts("Off", "On")
        chTrig_layout.addWidget(chEnable, row, col + 1)
        self.pvWidgetList.append(chEnable)

      pv = self.FindChannelPV(i, "led_threshold")
      if pv is not None:
        chThreshold = RLineEdit(pv, width=65, parent=self)
        chTrig_layout.addWidget(chThreshold, row, col + 2)
        self.pvWidgetList.append(chThreshold)

      pv = self.FindChannelPV(i, "disc_count")
      if pv is not None:
        chTrigger = RLineEdit(pv, width=80, parent=self)
        chTrig_layout.addWidget(chTrigger, row, col + 3)
        self.pvWidgetList.append(chTrigger)

      pv = self.FindChannelPV(i, "ahit_count")
      if pv is not None:
        chAccepted = RLineEdit(pv, width=80, parent=self)
        chTrig_layout.addWidget(chAccepted, row, col + 4)
        self.pvWidgetList.append(chAccepted)

      pv = self.FindChannelPV(i, "downsample_factor")
      if pv is not None:
        chDownSample = RComboBox(pv, width=80, parent=self)
        chTrig_layout.addWidget(chDownSample, row, col + 5)
        self.pvWidgetList.append(chDownSample)

    row += 1
    col = 0
    chTrig_layout.addWidget(GLabel("All Ch.", alignment=Qt.AlignmentFlag.AlignRight), row, col, 1, 2)
    allChThreshold = GLineEdit("", parent=self)
    allChThreshold.setFixedWidth(65)
    allChThreshold.returnPressed.connect(lambda: [self.FindChannelPV(i, "led_threshold").SetValue(int(allChThreshold.text())) for i in range(10)])
    chTrig_layout.addWidget(allChThreshold, row, col + 2)

    chTrig_layout.addWidget(GLabel("Counter Mode", alignment=Qt.AlignmentFlag.AlignRight), row, col + 3, 1, 2)
    counterMode = RComboBox(self.FindPV("counter_mode"),  parent=self)
    chTrig_layout.addWidget(counterMode, row, col + 5)
    self.pvWidgetList.append(counterMode)

    row += 1
    col = 1
    openChannel = QPushButton("Open Channel", parent=self)
    openChannel.setFixedHeight(60)
    openChannel.clicked.connect(self.OpenChannelWindow)
    chTrig_layout.addWidget(openChannel, row, col, 1, 4)

    #&================================ Throttle Control
    groupBox_throttle = QGroupBox("Throttle Control")
    throttle_layout = QGridLayout()
    throttle_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_throttle.setLayout(throttle_layout)

    pvNameList = [
      ["rj45_throttle_mode", "Throttle Mode",       False],
      ["lfsr_rate_sel",      "LFSR rate",           False],
      ["FIFO_Prog_Thresh",   "Prog. Throttle Mode", False],
      ["lfsr_seed",          "LFSR seed",           False]
    ]
    self.FillWidgets(throttle_layout, pvNameList, maxRows=8, widgetWidth=80)


    #&================================ Board Control
    groupBox_control = QGroupBox("Board Control")
    control_layout = QGridLayout()
    control_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_control.setLayout(control_layout)

    control_pvNameList = [
      ["master_logic_enable",      "Master Logic",            False],
      ["CS_Ena",                   "Readout",                 False],
      ["trigger_mux_select",       "Trig Mode",               False],
      ["cfd_mode",                 "CFD Mode",                False],
      ["win_comp_min",             "Comp. Win Min [us]",      False],
      ["win_comp_max",             "Comp. Win Max [us]",      False],
      ["veto_enable",              "Veto",                    False],
      ["clk_select",               "Clock Scr",               False],
      ["sd_sm_lost_lock_flag_rst", "Reset Lost Lock",         False],
      ["ext_disc_ts_sel",          "Ext Disc. TS",            False],
      ["reg_downsample_holdoff",   "Reg Downsample Holdoff",  False],
      ["diag_mux_control",         "Diag. Mux Control",       False],
      ["DIAG_WAVE_SEL",            "Diag. Wave Select",       False],
      ["EXT_DISC_REQ",             "VME Disc. Req.",          False]
    ]
    self.FillWidgets(control_layout, control_pvNameList, maxRows=14, widgetWidth=100)

    #&================================ ADC Status
    adc_pvNameList = [
      ["adc_ph_shift_overflow", "Phase Shift Overflow", False],
      ["adc_dcm_clock_stopped", "DCM clock stopped",    False],
      ["adc_dcm_reset",         "DCM Reset",            False],
      ["adc_dcm_lock",          "DCM Lock",             False],
      ["adc_dcm_ctrl_status",   "DCM Ctrl Status",      False]
    ]

    groupBox_adc = QGroupBox("ADC Status")
    adc_layout = QGridLayout()
    adc_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
    groupBox_adc.setLayout(adc_layout)

    self.FillWidgets(adc_layout, adc_pvNameList, maxRows=8, widgetWidth=60)

    #&================================ ACQ Status
    acq_pvNameList = [
      ["acq_ph_shift_overflow", "Phase Shift Overflow", False],
      ["acq_dcm_clock_stopped", "DCM clock stopped",    False],
      ["acq_dcm_reset",         "DCM Reset",            False],
      ["acq_dcm_lock",          "DCM Lock",             False],
      ["acq_dcm_ctrl_status",   "DCM Ctrl Status",      False]
    ]

    groupBox_acq = QGroupBox("Acquisition Status")
    acq_layout = QGridLayout()
    acq_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
    groupBox_acq.setLayout(acq_layout)

    self.FillWidgets(acq_layout, acq_pvNameList, maxRows=8, widgetWidth=60)

    #&================================ Phase Status
    phase_pvNameList = [
      ["ph_checking",      "Phase Check",    False],
      ["ph_hunting_down", "Hunting Down",    False],
      ["ph_hunting_up",   "Hunting Up",      False],
      ["ph_failure",     "Phase Failure",    False],
      ["ph_success",     "Phase Success",    False]
    ]

    groupBox_phase = QGroupBox("Phase Status")
    phase_layout = QGridLayout()
    phase_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
    groupBox_phase.setLayout(phase_layout)

    self.FillWidgets(phase_layout, phase_pvNameList, maxRows=8, widgetWidth=60)

    #================================= Layout of groups
    layout.addWidget(groupBox_info,     0, 0, 2, 1)
    layout.addWidget(groupBox_serdes,   0, 1, 2, 1)

    layout.addWidget(groupBox_fifo,     0, 2, 1, 1)
    layout.addWidget(groupBox_throttle, 1, 2, 1, 1)

    layout.addWidget(groupBox_chTrig,   2, 0, 3, 1)
    layout.addWidget(groupBox_control,  2, 1, 3, 1)

    layout.addWidget(groupBox_adc,      2, 2, 1, 1)
    layout.addWidget(groupBox_acq,      3, 2, 1, 1)
    layout.addWidget(groupBox_phase,    4, 2, 1, 1)

    #================================ QTimer for updating PVs
    self.timer = QTimer()
    self.timer.timeout.connect(self.UpdatePVs)
    self.timer.start(500)  # Update every 1000 milliseconds (1 second

  #################################################################
  def closeEvent(self, a0):
    if self.chWindows is not None:
      self.chWindows.close()
    return super().closeEvent(a0) 

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
  
  def OpenChannelWindow(self):

    if self.chWindows is None:
      self.chWindows = CHWindow(f"{self.board.BD_name} - Channel", self.board)
    
    self.chWindows.show()
    self.chWindows.raise_()
    self.chWindows.activateWindow()

  def FillWidgets(self, layout: QGridLayout, pvNameList, maxRows = 9, widgetWidth = 100):

    row = 0
    col = 0

    for pvName, displayName, isHex in pvNameList:
      pv = self.FindPV(pvName)
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

  def UpdatePVs(self):
    if not self.isVisible():
      return
    for pvWidget in self.pvWidgetList:

      force = False
      if self.isACQRunning:
        pvName = pvWidget.pv.name.split(":")[-1]
        if pvName in ["led_threshold", "channel_enable", "disc_count", "ahit_count"] :
          force = True

      pvWidget.UpdatePV(force)
