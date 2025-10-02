from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget, QGroupBox, QPushButton, QFrame, QComboBox, QLabel
from PyQt6.QtCore import Qt, QTimer

from class_Board import Board
from class_PV import PV
from custom_QClasses import GLabel, GLineEdit
from class_PVWidgets import RRegisterDisplay, RLineEdit, RTwoStateButton, RComboBox, RMapTwoStateButton, RLabelLineEdit, RSetButton, RMapLineEdit
from gui_RAM import RAMWindow
import re

from aux import make_pattern_list, natural_key

from gui_MTRG import templateTab


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

    #&================================ Board Info
    pvNameList = [
      ["regin_code_revision",            "Code Revision",     True,  "lineEdit"],
      ["code_date",                      "Code Date",         True,  "lineEdit"],
      ["vme_code_revision",              "VME Code Rev.",     True,  "lineEdit"],
      ["serial_num",                     "Serial No.",        True,  "lineEdit"],
      ["live_timestamp_msb",             "Timestamp MSB",     True,  "lineEdit"],
      ["live_timestamp_lsb",             "Timestamp LSB",     True,  "lineEdit"],  
      ["geo_addr",                       "Geo Addr",          False, "lineEdit"],
      ["user_package_data",              "Board ID",          False, "lineEdit"],
      ["fw_type",                        "FW Type",           False, "lineEdit"],
      ["reg_led_state",                  "LED State",         True,  "lineEdit"], 
      ["power_ok",                       "Power OK",          False, "twoState" ],
      ["over_volt_stat",                 "Over Volt Stat",    False, "twoState" ],
      ["under_volt_stat",                "Under Volt Stat",   False, "twoState" ],
      ["temp0_sensor",                   "Temp Sensor 0",     False, "twoState" ],
      ["temp1_sensor",                   "Temp Sensor 1",     False, "twoState" ],
      ["temp2_sensor",                   "Temp Sensor 2",     False, "twoState" ],
      ["reg_master_logic_status",        "Misc. Log. Status", True,  "lineEdit" ],
      ["reg_sd_config",                  "SD Config",         True,  "lineEdit" ],
      ["vme_gp_ctrl",                    "VME gp Ctrl",       True,  "lineEdit" ],
      ["reg_external_discriminator_src", "Ext. Disc. Src",    True,  "lineEdit" ],
      ["reg_external_disc_mode",         "Ext. Disc. Mode",   True,  "lineEdit" ],
      ["regin_ts_err_count",             "TS Err Count",      True,  "lineEdit" ]
    ]

    groupBox_info = QGroupBox("Board Info / Status")
    info_layout = QGridLayout()
    info_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_info.setLayout(info_layout)
    
    self.FillWidgets(info_layout, pvNameList, maxRows = 11, widgetWidth = 120)

    #&================================ Serders Status/Control
    pvNameList = [
      ["serdes_lock",                    "SerDes Lock",       False, "twoState" ],
      ["serdes_sm_locked",               "SM Locked",         False, "twoState" ],
      ["serdes_sm_lost_lock_flag",       "Lost Lock Flag",    False, "twoState" ],
      ["sd_rx_pwr",                      "Rx Pwr",            False, "twoState" ],
      ["sd_tx_pwr",                      "Tx Pwr",            False, "twoState" ],
      ["sd_local_loopback_en",           "Local Loopback",    False, "twoState" ],
      ["sd_line_loopback_en",            "Line Loopback",     False, "twoState" ],
      ["sd_pem",                         "PEM",               False, "twoState" ],
      ["sd_sync",                        "Sync",              False, "twoState" ],
      ["sd_sm_stringent_lock",           "Strngnt Lock",      False, "twoState" ]
    ]

    groupBox_serdes = QGroupBox("SerDes Status/Control")
    serdes_layout = QGridLayout()
    serdes_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
    groupBox_serdes.setLayout(serdes_layout)

    self.FillWidgets(serdes_layout, pvNameList, maxRows = 10, widgetWidth = 100)


    #&================================ FIFO Status/Control
    pvNameList = [
      ["master_fifo_reset",              "Master FIFO Reset",  False, "twoState" ],
      ["fifo_a_empty",                   "FIFO A Empty",      False, "twoState" ],
      ["fifo_b_empty",                   "FIFO B Empty",      False, "twoState" ],
      ["fifo_a_full",                    "FIFO A Full",       False, "twoState" ],
      ["fifo_b_full",                    "FIFO B Full",       False, "twoState" ],
      ["fifo_fulla",                     "FIFO Full A",       False, "twoState" ],
      ["fifo_fullb",                     "FIFO Full B",       False, "twoState" ],
      ["fifo_almost_full",               "FIFO Almost Full",  False, "twoState" ],
      ["ini_fifo_prog_flag",             "FIFO Prog. Flag",   False, "twoState" ],
      ["fifo_depth",                     "FIFO Depth",        True,  "lineEdit" ],
      ["int_FIFO_PROG_ERR",              "FIFO Prog. Err",    False, "twoState" ],
      ["int_FIFO_PROG_FLG",              "FIFO Prog. Flg",    False, "twoState" ]
    ]

    groupBox_fifo = QGroupBox("FIFO Status/Control")
    fifo_layout = QGridLayout()
    fifo_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_fifo.setLayout(fifo_layout)

    self.FillWidgets(fifo_layout, pvNameList, maxRows = 9, widgetWidth = 100)

    #&================================ Channel Triggers/Controls
    groupBox_chTrig = QGroupBox("Channel Triggers/Controls")
    chTrig_layout = QGridLayout()
    chTrig_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_chTrig.setLayout(chTrig_layout)

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
    col = 0
    chTrig_layout.addWidget(GLabel("Open Channel", alignment=Qt.AlignmentFlag.AlignRight), row, col, 1, 2)
    openChannel = QComboBox(parent=self)
    openChannel.setFixedWidth(65)
    openChannel.addItem("None")
    for i in range(10):
      openChannel.addItem(f"Ch-{i}")
    openChannel.currentIndexChanged.connect(lambda index:
                                             print(f"Open Channel: {index-1}") 
    )
    chTrig_layout.addWidget(openChannel, row, col + 2)

    #&================================ Throttle Control
    groupBox_throttle = QGroupBox("Throttle Control")
    throttle_layout = QGridLayout()
    throttle_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_throttle.setLayout(throttle_layout)

    pvNameList = [
      ["rj45_throttle_mode", "Throttle Mode", False, "lineEdit"],
      ["lfsr_rate_sel", "LFSR rate", False, "lineEdit"],
      ["FIFO_Prog_Thresh", "Prog. Throttle Mode", False, "lineEdit"],
      ["lfsr_seed", "LFSR seed", False, "lineEdit"]
    ]
    self.FillWidgets(throttle_layout, pvNameList, maxRows=8, widgetWidth=80)


    #&================================ Board Control
    groupBox_control = QGroupBox("Board Control")
    control_layout = QGridLayout()
    control_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_control.setLayout(control_layout)

    control_pvNameList = [
      ["master_logic_enable",      "Master Logic",            False, "twoState"],
      ["CS_Ena",                   "Readout",                 False, "twoState"],
      ["trigger_mux_select",       "Trig Mode",               False, "comboBox"],
      ["cfd_mode",                 "CFD Mode",                False, "comboBox"],
      ["win_comp_min",             "Comp. Win Min [us]",      False, "lineEdit"],
      ["win_comp_max",             "Comp. Win Max [us]",      False, "lineEdit"],
      ["veto_enable",              "Veto",                    False, "twoState"],
      ["clk_select",               "Clock Scr",               False, "twoState"],
      ["sd_sm_lost_lock_flag_rst", "Reset Lost Lock",         False, "twoState"],
      ["ext_disc_ts_sel",          "Ext Disc. TS",            False, "comboBox"],
      ["reg_downsample_holdoff",   "Reg Downsample Holdoff",  False, "lineEdit"],
      ["diag_mux_control",         "Diag. Mux Control",       False, "comboBox"],
      ["DIAG_WAVE_SEL",            "Diag. Wave Select",       False, "comboBox"],
      ["EXT_DISC_REQ",             "VME Disc. Req.",          False, "twoState"]
    ]
    self.FillWidgets(control_layout, control_pvNameList, maxRows=14, widgetWidth=120)

    #&================================ ADC Status
    adc_pvNameList = [
      ["adc_ph_shift_overflow", "Phase Shift Overflow", False, "lineEdit"],
      ["adc_dcm_clock_stopped", "DCM clock stopped",    False, "lineEdit"],
      ["adc_dcm_reset",         "DCM Reset",            False, "lineEdit"],
      ["adc_dcm_lock",          "DCM Lock",             False, "lineEdit"],
      ["adc_dcm_ctrl_status",   "DCM Ctrl Status",      False, "lineEdit"]
    ]

    groupBox_adc = QGroupBox("ADC Status")
    adc_layout = QGridLayout()
    adc_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_adc.setLayout(adc_layout)

    self.FillWidgets(adc_layout, adc_pvNameList, maxRows=8, widgetWidth=120)

    #&================================ ACQ Status
    acq_pvNameList = [
      ["acq_ph_shift_overflow", "Phase Shift Overflow", False, "lineEdit"],
      ["acq_dcm_clock_stopped", "DCM clock stopped",    False, "lineEdit"],
      ["acq_dcm_reset",         "DCM Reset",            False, "lineEdit"],
      ["acq_dcm_lock",          "DCM Lock",             False, "lineEdit"],
      ["acq_dcm_ctrl_status",   "DCM Ctrl Status",      False, "lineEdit"]
    ]

    groupBox_acq = QGroupBox("Acquisition Status")
    acq_layout = QGridLayout()
    acq_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_acq.setLayout(acq_layout)

    self.FillWidgets(acq_layout, acq_pvNameList, maxRows=8, widgetWidth=120)

    #&================================ Phase Status
    phase_pvNameList = [
      ["ph_checking",      "Phase Check",      False, "lineEdit"],
      ["ph_hunting_down", "Hunting Down",    False, "lineEdit"],
      ["ph_hunting_up",   "Hunting Up",      False, "lineEdit"],
      ["ph_failure",     "Phase Failure",    False, "lineEdit"],
      ["ph_success",     "Phase Success",    False, "lineEdit"]
    ]

    groupBox_phase = QGroupBox("Phase Status")
    phase_layout = QGridLayout()
    phase_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    groupBox_phase.setLayout(phase_layout)

    self.FillWidgets(phase_layout, phase_pvNameList, maxRows=8, widgetWidth=120)

    #================================= Layout of groups
    rowIdx = 0
    colIdx = 0

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
  
  def FillWidgets(self, layout: QGridLayout, pvNameList, maxRows = 9, widgetWidth = 100):

    row = 0
    col = 0

    for pvName, displayName, isHex, type in pvNameList:
      pv = self.FindPV(pvName)
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
    # if not self.isActiveWindow() or not self.isVisible():
    #   return

    for pvWidget in self.pvWidgetList:
      pvWidget.UpdatePV()

    # current_tab = self.tabs.currentWidget()
    # if current_tab is self.tab1:
    #   self.tab1.UpdatePVs()
    # elif current_tab is self.tab2:
    #   self.tab2.UpdatePVs()
