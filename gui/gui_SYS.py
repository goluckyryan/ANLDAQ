from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget, QTabWidget, QGroupBox, QPushButton, QFrame, QComboBox, QLabel
from PyQt6.QtCore import Qt, QTimer

from class_Board import Board
from class_PV import PV
from custom_QClasses import GLabel, GLineEdit
from class_PVWidgets import RLineEdit, RTwoStateButton, RMapTwoStateButton, RRegisterDisplay, RComboBox

from aux import make_pattern_list
import re

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

      pvWidget.UpdatePV(forced)

#@===================================================================================
class sysTimestampReadOutTab(sysTemplateTab):
  def __init__(self, MTRG : Board, RTR_list, DIG_list, parent=None):
    super().__init__(MTRG, RTR_list, DIG_list, parent)

    layout = QGridLayout()
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.setLayout(layout)

    #&=========================== Create a group box for Timestamp Readout
    timestampGroup = QGroupBox("Timestamp")
    groupLayout = QGridLayout()
    groupLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    timestampGroup.setLayout(groupLayout)

    row = 0

    groupLayout.addWidget(QLabel("Imp Sync"), row, 2)
    btn_ImpSync = RTwoStateButton(self.FindPV("IMP_SYNC", self.MTRG))
    self.pvWidgetList.append(btn_ImpSync)
    groupLayout.addWidget(btn_ImpSync, row, 3)

    #/================ MTRG Timestamp
    row += 1
    groupLayout.addWidget(GLabel("MTRG"), row, 0)

    le_mtrg_timeA = RLineEdit(self.FindPV("reg_TIMESTAMP_A",self.MTRG),  hexBinDec = "hex", width=90)
    le_mtrg_timeB = RLineEdit(self.FindPV("reg_TIMESTAMP_B",self.MTRG),  hexBinDec = "hex", width=90)
    le_mtrg_timeC = RLineEdit(self.FindPV("reg_TIMESTAMP_C",self.MTRG),  hexBinDec = "hex", width=90)
    mtrg_clk_src = RTwoStateButton(self.FindPV("ClkSrc", self.MTRG))

    self.pvWidgetList.append(le_mtrg_timeA)
    self.pvWidgetList.append(le_mtrg_timeB)
    self.pvWidgetList.append(le_mtrg_timeC)
    self.pvWidgetList.append(mtrg_clk_src)

    groupLayout.addWidget(le_mtrg_timeA, row, 1)
    groupLayout.addWidget(le_mtrg_timeB, row, 2)
    groupLayout.addWidget(le_mtrg_timeC, row, 3)
    groupLayout.addWidget(mtrg_clk_src, row, 4)

    #/================ RTR Timestamp
    row += 1

    for i, rtr in enumerate(self.RTR_list):
      groupLayout.addWidget(GLabel(f"RTR-{i}"), row, 0)

      le_rtr_timeA = RLineEdit(self.FindPV("reg_TIMESTAMP_A", rtr), hexBinDec = "hex", width=90)
      le_rtr_timeB = RLineEdit(self.FindPV("reg_TIMESTAMP_B", rtr), hexBinDec = "hex", width=90)
      le_rtr_timeC = RLineEdit(self.FindPV("reg_TIMESTAMP_C", rtr), hexBinDec = "hex", width=90)
      rtr_clk_src = RTwoStateButton(self.FindPV("ClkSrc", rtr))

      self.pvWidgetList.append(le_rtr_timeA)
      self.pvWidgetList.append(le_rtr_timeB)
      self.pvWidgetList.append(le_rtr_timeC)
      self.pvWidgetList.append(rtr_clk_src)

      groupLayout.addWidget(le_rtr_timeA, row, 1)
      groupLayout.addWidget(le_rtr_timeB, row, 2)
      groupLayout.addWidget(le_rtr_timeC, row, 3)
      groupLayout.addWidget(rtr_clk_src, row, 4)
      row += 1

    #/================ DIG Timestamp

    for i, dig in enumerate(self.DIG_list):
      groupLayout.addWidget(GLabel(f"DIG-{i}"), row, 0)

      le_dig_timeA = RLineEdit(self.FindPV("live_timestamp_msb", dig), hexBinDec = "hex", width=90)
      le_dig_timeB = RLineEdit(self.FindPV("live_timestamp_lsb", dig), hexBinDec = "hex", width=90)
      dig_clk_src = RTwoStateButton(self.FindPV("clk_select", dig))

      self.pvWidgetList.append(le_dig_timeA)
      self.pvWidgetList.append(le_dig_timeB)
      self.pvWidgetList.append(dig_clk_src)

      groupLayout.addWidget(le_dig_timeA, row, 1)
      groupLayout.addWidget(le_dig_timeB, row, 2)
      groupLayout.addWidget(dig_clk_src, row, 4)
      row += 1

    # Add the group box to the main layout
    layout.addWidget(timestampGroup, 0, 0, 1, 1)

    #&=========================== Create a group box for Readout Status
    readoutGroup = QGroupBox("Readout")
    readoutLayout = QGridLayout()
    readoutLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    readoutGroup.setLayout(readoutLayout)
    
    pvName = "CS_Ena"

    row = 0
    readoutLayout.addWidget(GLabel("MTRG"), row, 0)
    mtrg_Ena = RTwoStateButton(self.FindPV(pvName, self.MTRG))
    self.pvWidgetList.append(mtrg_Ena)
    readoutLayout.addWidget(mtrg_Ena, row, 1)

    row += 1
    readoutLayout.addWidget(GLabel("MTRG FIFO"), row, 0)
    mtrg_fifo_Ena = RComboBox(self.FindPV("FifoNum", self.MTRG))
    self.pvWidgetList.append(mtrg_fifo_Ena)
    readoutLayout.addWidget(mtrg_fifo_Ena, row, 1)

    for i, dig in enumerate(self.DIG_list):
      row += 1
      readoutLayout.addWidget(GLabel(f"DIG-{i}"), row, 0)
      dig_Ena = RTwoStateButton(self.FindPV(pvName, dig))
      self.pvWidgetList.append(dig_Ena)
      readoutLayout.addWidget(dig_Ena, row, 1)

    layout.addWidget(readoutGroup, 0, 1, 1, 1)

    #&================ Update QTimer
    # self.forceUpdateOn = True
    self.timer.start(500)  # Update every 1000 milliseconds (1 second


#@===================================================================================
class sysLinktab(sysTemplateTab):
  def __init__(self, MTRG : Board, RTR_list, parent=None):
    super().__init__(MTRG, RTR_list, None, parent)

    layout = QGridLayout()
    self.setLayout(layout)


    #&================ Link Status
    linkStatusGroup = QGroupBox("Link Status")
    groupLayout = QGridLayout()
    linkStatusGroup.setLayout(groupLayout)

    groupLayout.addWidget(GLabel("MTRG", alignment=Qt.AlignmentFlag.AlignRight), 0, 0)
    mtr_status = RRegisterDisplay(self.FindPV("reg_MISC_STAT", self.MTRG), isRTR = False)
    self.pvWidgetList.append(mtr_status)
    groupLayout.addWidget(mtr_status, 1, 0, 10, 1, Qt.AlignmentFlag.AlignRight)

    for i, rtr in enumerate(self.RTR_list):
      if i == 0 :
        groupLayout.addWidget(GLabel(f"RTR-{i}", alignment=Qt.AlignmentFlag.AlignRight), 0, i+1)
      else:
        groupLayout.addWidget(GLabel(f"{i}", alignment=Qt.AlignmentFlag.AlignRight), 0, i+1)
      showRowLabel = (i == 0)
      rtr_status = RRegisterDisplay(self.FindPV("reg_MISC_STAT_REG", rtr), isRTR = True, showRowLabel = showRowLabel)
      self.pvWidgetList.append(rtr_status)
      groupLayout.addWidget(rtr_status, 1, i+1, 10, 1, Qt.AlignmentFlag.AlignRight)

    layout.addWidget(linkStatusGroup, 0, 0, 3, 1)

    #&================ Link Lock statusW
    linkLockGroup = QGroupBox("Link Lock Status")
    lockLayout = QGridLayout()
    linkLockGroup.setLayout(lockLayout)

    row = 0
    col = 0

    lock_pvNameList = ["LOCK_A", "LOCK_B", "LOCK_C", "LOCK_D", "LOCK_E", "LOCK_F", "LOCK_G", "LOCK_H", "LOCK_L", "LOCK_R", "LOCK_U"]
    mtrg_pvList = [self.FindPV(pv_name, self.MTRG) for pv_name in lock_pvNameList]

    linkM = RMapTwoStateButton(mtrg_pvList, rows=1, cols=len(mtrg_pvList), customRowLabel="MTRG", rowLabelLen=60, parent=self)
    linkM.SetInvertStateColor(True)
    self.pvWidgetList.append(linkM)
    lockLayout.addWidget(linkM, row, col, 1, 2)

    row += 1
    for i, rtr in enumerate(self.RTR_list):
      rtr_pvList = [self.FindPV(pv_name, rtr) for pv_name in lock_pvNameList]
      linkR = RMapTwoStateButton(rtr_pvList, rows=1, cols=len(rtr_pvList), hasColLabel=False, customRowLabel=f"RTR-{i}", rowLabelLen=60, parent=self)
      linkR.SetInvertStateColor(True)
      self.pvWidgetList.append(linkR)
      lockLayout.addWidget(linkR, row, col, 1, 2)
      row += 1

    # Add the group box to the main layout
    layout.addWidget(linkLockGroup, 0, 1, 1, 1)

    #&================ Input Link Mask
    linkMaskGroup = QGroupBox("Input Link Mask")
    maskLayout = QGridLayout()
    linkMaskGroup.setLayout(maskLayout)

    row = 0
    col = 0

    LIM_pvNameList = ["ILM_A", "ILM_B", "ILM_C", "ILM_D", "ILM_E", "ILM_F", "ILM_G", "ILM_H", "ILM_L", "ILM_R", "ILM_U"]
    mtrg_pvList = [self.FindPV(pv_name, self.MTRG) for pv_name in LIM_pvNameList]

    linkM = RMapTwoStateButton(mtrg_pvList, rows=1, cols=len(mtrg_pvList), customRowLabel="MTRG", rowLabelLen=60, parent=self)
    linkM.SetInvertStateColor(True)
    self.pvWidgetList.append(linkM)
    maskLayout.addWidget(linkM, row, col, 1, 2)

    row += 1
    for i, rtr in enumerate(self.RTR_list):
      rtr_pvList = [self.FindPV(pv_name, rtr) for pv_name in LIM_pvNameList]
      linkR = RMapTwoStateButton(rtr_pvList, rows=1, cols=len(rtr_pvList), hasColLabel=False, customRowLabel=f"RTR-{i}", rowLabelLen=60, parent=self)
      linkR.SetInvertStateColor(True)
      self.pvWidgetList.append(linkR)
      maskLayout.addWidget(linkR, row, col, 1, 2)
      row += 1

    layout.addWidget(linkMaskGroup, 1, 1, 1, 1)

    #&================ Link Control
    linkControlGroup = QGroupBox("Link L Control")
    controlLayout = QGridLayout()
    linkControlGroup.setLayout(controlLayout)

    row = 0
    controlLayout.addWidget(GLabel("MTRG", alignment=Qt.AlignmentFlag.AlignRight), row, 0, 1, 2)

    row = 1
    col = 0

    mtrg_LLC_pvNameList = ["LOCK_RETRY", "LOCK_ACK", "RESET_LINK_INIT", "LINK_L_STRINGENT",  "LINK_R_STRINGENT", "LINK_U_STRINGENT", ""]
    mtrg_pvList = [self.FindPV(pv_name, self.MTRG) for pv_name in mtrg_LLC_pvNameList]

    pvNameLabels = ["Lock Retry", "Lock Ack", "Reset Link Init", "Link L Stringent",  "Link R Stringent", "Link U Stringent", "Reset Lock Lost"]

    for i, pv in enumerate(mtrg_pvList):
      name = pvNameLabels[i]
      controlLayout.addWidget(GLabel(name + "  ", alignment=Qt.AlignmentFlag.AlignRight), row, col)
      if pv is None:
        row += 1
        continue
      btn = RTwoStateButton(pv, width=30)
      self.pvWidgetList.append(btn)
      controlLayout.addWidget(btn, row, col+1)
      row += 1

    row = 1
    col += 1
    rtrg_LLC_pvNameList = ["LOCK_RETRY", "LOCK_ACK", "RESET_LINK_INIT", "STRINGENT_LOCK",  "", "", "SM_LOST_LOCK_RESET"]


    for j, rtr in enumerate(self.RTR_list):
      rtrg_pvList = [self.FindPV(pv_name, rtr) for pv_name in rtrg_LLC_pvNameList]
      col += 1
      controlLayout.addWidget(GLabel(f"RTR\n{j}", alignment=Qt.AlignmentFlag.AlignHCenter), 0, col)
      for i, pv in enumerate(rtrg_pvList):
        if pv is None:
          row += 1  
          continue
        btn = RTwoStateButton(pv, width=30)
        self.pvWidgetList.append(btn)
        controlLayout.addWidget(btn, row, col)
        row += 1


    layout.addWidget(linkControlGroup, 2, 1)


    #&================ Update QTimer
    self.timer.start(500)  # Update every 1000 milliseconds (1 second


#@===================================================================================
class globalSettingTab(sysTemplateTab):
  def __init__(self, MTRG : Board, RTR_list, DIG_list, parent=None):
    super().__init__(MTRG, RTR_list, DIG_list, parent)

    layout = QGridLayout()
    self.setLayout(layout)


