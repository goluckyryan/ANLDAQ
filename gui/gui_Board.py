from PyQt6.QtWidgets import QMainWindow, QGridLayout, QComboBox, QWidget, QGroupBox, QLabel, QPushButton
from PyQt6.QtWidgets import QApplication

from class_Board import Board
from class_PV import PV  # Make sure to import PV if not already

from custom_QClasses import GLineEdit, GTwoStateButton, GLabel
from PyQt6.QtCore import QTimer, Qt

from class_PVWidgets import RLineEdit, RTwoStateButton, RComboBox, RMapTwoStateButton, RMapLineEdit, RRegisterDisplay

from gui_RAM import RAMWindow

import re

from aux import make_pattern_list, natural_key

class BoardPVWindow(QMainWindow):
  def __init__(self, board_name,  board : Board, channelNo = -1, parent=None):
    super().__init__(parent)
    self.board_name = board_name
    self.channelNo = channelNo
    self.Board = board

    self.setWindowTitle(f"Generic | {board_name}")
    self.setGeometry(150, 150, 300, 400)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #=============================== GUI setup
    rowIndex = 0
    colIndex = 0
    maxRows = int(40)

    if board.NumChannels > 0 and channelNo < 0:
      layout.addWidget(GLabel("Channel :"), rowIndex, colIndex)
      self.combo_chSel = QComboBox()
      self.combo_chSel.addItem("Select Channel")
      for i in range(board.NumChannels):
        self.combo_chSel.addItem(f"Channel {i}")
      self.combo_chSel.setCurrentIndex(0)
      self.combo_chSel.currentIndexChanged.connect(self.OnChannelChanged)
      layout.addWidget(self.combo_chSel, rowIndex, colIndex + 1)
      rowIndex += 1

    if channelNo >= 0 and board.NumChannels > 0:
      pv_list = board.CH_PV[channelNo]
    else:
      pv_list = board.Board_PV
    
    map_pv = ["XMAP_", "YMAP_", "DISCRIMINATOR_DELAY"]
    self.hasMap = False
    map_pvList = [[] for _ in range(len(map_pv))]

    link_pv = [ "LOCK",  "DEN",  "REN",  "SYNC", "RPwr", "TPwr", "SLiL", "SLoL", "ILM", "LINK", "GATED_THROTTLE", 'RAW_THROTTLE' ] # the last three only for RTR
    self.hasLink = False
    link_pvList = [[] for _ in range(len(link_pv))]
    link_patterns = make_pattern_list(link_pv)

    diag_pv = ["Diag_", "LOCK_COUNT" ]
    self.hasDiag = False
    diag_pvList = [[] for _ in range(len(diag_pv))]

    fifoReset_pv = ["FIFOReset"]
    self.hasFifoReset = False
    fifoReset_pvList = [[] for _ in range(len(fifoReset_pv))]

    ram_pv = ["VETO_RAM", "TRIG_RAM", "SWEEP_RAM"]
    not_ram_pv = ["VETO_RAM_ADDR_SRC", "TRIG_RAM_ADDR_SRC", "SWEEP_RAM_ADDR_SRC"]
    self.hasRam = False
    self.ram_pvList = [[] for _ in range(len(ram_pv))]

    mtrg_link_pv = ["LINK_L_PROPAGATE", "LINK_R_PROPAGATE", "LINK_U_PROPAGATE"]
    self.hasMTRGLink = False
    mtrg_link_pvList = [[] for _ in range(len(mtrg_link_pv))]

    veto_pv = ["EN_NIM_VETO_", "EN_RAM_VETO_", "EN_REMTRIG_VETO_", "EN_SOFTWARE_VETO_", "EN_THROTTLE_VETO_"]
    self.hasVeto = False
    veto_pvList = [[] for _ in range(len(veto_pv))]

    self.isRTR = False
    rtrReg_pv = None
    self.isMTRG = False
    mtrgReg_pv = None


    #========================== General PVs widgets
    for i, pv in enumerate(pv_list):
      if not isinstance(pv, PV):
        continue
      pvName = pv.name.split(":")[-1]

      if any(pvName.startswith(prefix) for prefix in map_pv):
        if not self.hasMap:
          self.hasMap = True
        for j , map_pv_item in enumerate(map_pv):
          if pvName.startswith(map_pv_item):
            map_pvList[j].append(pv)
        continue

      if any(pattern.match(pvName) for pattern in link_patterns):
        if not self.hasLink:
          self.hasLink = True
        for j , link_pv_item in enumerate(link_pv):
          if pvName.startswith(link_pv_item):
            link_pvList[j].append(pv)
        continue


      if any(pvName.startswith(prefix) for prefix in fifoReset_pv):
        if not self.hasFifoReset:
          self.hasFifoReset = True
        for j , fifoReset_pv_item in enumerate(fifoReset_pv):
          if pvName.startswith(fifoReset_pv_item):
            fifoReset_pvList[j].append(pv)
        continue

      if any(pvName.startswith(prefix) for prefix in diag_pv):
        if not self.hasDiag:
          self.hasDiag = True
        for j , diag_pv_item in enumerate(diag_pv):
          if pvName.startswith(diag_pv_item):
            diag_pvList[j].append(pv)
        continue

      if any(pvName.startswith(prefix) for prefix in ram_pv) and pvName not in not_ram_pv:
        if not self.hasRam:
          self.hasRam = True
        for j , ram_pv_item in enumerate(ram_pv):
          if pvName.startswith(ram_pv_item):
            self.ram_pvList[j].append(pv)
        continue

      if any(pvName.startswith(prefix) for prefix in mtrg_link_pv):
        if not self.hasMTRGLink:
          self.hasMTRGLink = True
        for j , mtrg_link_pv_item in enumerate(mtrg_link_pv):
          if pvName.startswith(mtrg_link_pv_item):
            mtrg_link_pvList[j].append(pv)
        continue

      if any(pvName.startswith(prefix) for prefix in veto_pv):
        if not self.hasVeto:
          self.hasVeto = True
        for j , veto_pv_item in enumerate(veto_pv):
          if pvName.startswith(veto_pv_item):
            veto_pvList[j].append(pv)
        continue

      if pvName == "reg_MISC_STAT" :
        self.isMTRG = True
        mtrgReg_pv = pv
        continue

      if pvName == "reg_MISC_STAT_REG" :
        self.isRTR = True
        rtrReg_pv = pv
        continue

      layout.addWidget(GLabel(f"{pvName}"), rowIndex, colIndex)

      if pv.NumStates() == 2:
        btn = RTwoStateButton(pv)
        btn.setProperty("idx", i)
        layout.addWidget(btn, rowIndex, colIndex + 1)

      elif pv.NumStates() > 2: #use RComboBox
        combo = RComboBox(pv)
        combo.setProperty("idx", i)
        layout.addWidget(combo, rowIndex, colIndex + 1)

      else:
        le = RLineEdit(pv, None, 100, parent=self)
        le.setProperty("idx", i)
        layout.addWidget(le, rowIndex, colIndex + 1)

      rowIndex += 1
      if rowIndex >= maxRows:
        rowIndex = 0
        colIndex += 2
    
    #========================== Special PVs widgets
    if self.hasRam:
      layout.addWidget(GLabel("RAM :"), rowIndex, colIndex)
      self.combo_ramSel = QComboBox()
      self.combo_ramSel.addItem("Select RAM")
      for i in range(len(ram_pv)):
        self.combo_ramSel.addItem(f"{ram_pv[i]}")
        self.ram_pvList[i].sort(key=lambda pv: natural_key(pv.name))
      self.combo_ramSel.setCurrentIndex(0)
      self.combo_ramSel.currentIndexChanged.connect(self.OnRamChanged)
      layout.addWidget(self.combo_ramSel, rowIndex, colIndex + 1)
      rowIndex += 1

    if self.hasFifoReset:

      groupBox_fifo = QGroupBox("FIFO Reset")
      fifo_layout = QGridLayout()
      groupBox_fifo.setLayout(fifo_layout)
      layout.addWidget(groupBox_fifo, rowIndex, colIndex, 13, 1 )

      self.fifoReset = RMapTwoStateButton(pvList = fifoReset_pvList[0], rows= len(fifoReset_pvList[0]), cols=1, clearText=False, hasRowLabel=True, hasColLabel=False, parent=self)
      fifo_layout.addWidget(self.fifoReset, 0, 0)


    if self.isRTR and rtrReg_pv is not None:
      groupBox_reg = QGroupBox("RTR Status")
      reg_layout = QGridLayout()
      reg_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
      groupBox_reg.setLayout(reg_layout)
      layout.addWidget(groupBox_reg, rowIndex, colIndex+1, 13, 1)

      self.rtrReg = RRegisterDisplay(rtrReg_pv, True, parent=self)
      reg_layout.addWidget(self.rtrReg, 0, 0)

    if self.isMTRG and mtrgReg_pv is not None:
      groupBox_reg = QGroupBox("MTRG Status")
      reg_layout = QGridLayout()
      reg_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
      groupBox_reg.setLayout(reg_layout)
      layout.addWidget(groupBox_reg, rowIndex, colIndex+1, 13, 1)

      self.mtrgReg = RRegisterDisplay(mtrgReg_pv, False, parent=self)
      reg_layout.addWidget(self.mtrgReg, 0, 0)

    rowIndex += 13      
    
    #------------------------- Link/Control
    if self.hasLink:
      rowIndex = 0
      colIndex += 2

      groupBox_Link = QGroupBox("Link")
      link_layout = QGridLayout()
      link_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
      groupBox_Link.setLayout(link_layout)
      layout.addWidget(groupBox_Link, rowIndex, colIndex, int(maxRows/2), 1 )

      self.linkWidgetList = []

      subRowIndex = 0
      for j , link_pv_item in enumerate(link_pv):
        if j  > 0 :
          showColLabel = False
        else:
          showColLabel = True
        
        if len(link_pvList[j]) == 0:
          continue

        link = RMapTwoStateButton(pvList = link_pvList[j], customRowLabel= link_pv_item, rowLabelLen=140, rows=1, hasColLabel=showColLabel, cols=len(link_pvList[j]), parent=self)
        if link_pv_item in ["LOCK", "ILM", "RAW_THROTTLE"]:
          link.SetInvertStateColor(True)
        link_layout.addWidget(link, subRowIndex, 0)
        self.linkWidgetList.append(link)
        subRowIndex += 1


    if self.hasDiag:

      self.diagWidgetList = []

      for j , diag_pv_item in enumerate(diag_pv):
        if j  > 0 :
          showColLabel = False
        else:
          showColLabel = True
        diag = RMapLineEdit(pvList = diag_pvList[j], customRowLabel= diag_pv_item, rows=1, hasColLabel=showColLabel, cols=len(diag_pvList[j]), parent=self)
        link_layout.addWidget(diag, subRowIndex, 0)
        subRowIndex += 1
        self.diagWidgetList.append(diag)

    if self.hasMTRGLink:

      self.mtrglinkWidgetList = []

      for j , mtrg_link_pv_item in enumerate(mtrg_link_pv):
        if j  > 0 :
          showColLabel = False
        else:
          showColLabel = True
        
        if len(mtrg_link_pvList[j]) == 0:
          continue

        link = RMapTwoStateButton(pvList = mtrg_link_pvList[j], customRowLabel= mtrg_link_pv_item, rowLabelLen=160,rows=1, hasColLabel=showColLabel, cols=len(mtrg_link_pvList[j]), parent=self)
        link_layout.addWidget(link, subRowIndex, 0)
        self.mtrglinkWidgetList.append(link)
        subRowIndex += 1

    if self.hasVeto:

      self.vetoWidgetList = []

      for j , veto_pv_item in enumerate(veto_pv):
        if j  > 0 :
          showColLabel = False
        else:
          showColLabel = True
        
        if len(veto_pvList[j]) == 0:
          continue

        veto = RMapTwoStateButton(pvList = veto_pvList[j], customRowLabel= veto_pv_item, rowLabelLen=200, rows=1, hasColLabel=showColLabel, cols=len(veto_pvList[j]), parent=self)
        link_layout.addWidget(veto, subRowIndex, 0)
        self.vetoWidgetList.append(veto)
        subRowIndex += 1

    #------------------------- Mapping
    if self.hasMap:
      rowIndex = int(maxRows/2)
      # colIndex += 2
    
      groupBox_map = QGroupBox("Mapping")
      map_layout = QGridLayout()
      map_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
      groupBox_map.setLayout(map_layout)
      layout.addWidget(groupBox_map, rowIndex, colIndex, int(maxRows/2), 1 )

      map_layout.addWidget(QLabel("X Map:"), 0, 0)
      self.xMap = RMapTwoStateButton(pvList = map_pvList[0], parent=self)
      map_layout.addWidget(self.xMap, 1, 0)

      map_layout.addWidget(QLabel("Y Map:"), 2, 0)
      self.yMap = RMapTwoStateButton(pvList = map_pvList[1], parent=self)
      map_layout.addWidget(self.yMap, 3, 0)

      map_layout.addWidget(QLabel("Discriminator Delay:"), 0, 1)
      self.ddMap = RMapLineEdit(pvList = map_pvList[2], parent=self)
      map_layout.addWidget(self.ddMap, 1, 1)

    # Set focus to none after GUI setup
    QApplication.focusWidget().clearFocus()

    #=============================== End of GUI setup

    self.ch_window = [[] for _ in range(board.NumChannels)]
    self.ram_window = [[] for _ in range(len(ram_pv))]

    self.timer = QTimer(self)
    self.timer.setInterval(500)  # check every 500 ms
    self.timer.timeout.connect(self.update_pvs)
    self.timer.start()

    self.EnableConnect = True

  #+++++++++++++++++++++++++++++++++++++++++++++++++++++
  def closeEvent(self, event):
    self.timer.stop()
    self.hide()
    event.ignore()  # Prevent actual deletion

  def update_pvs(self):
    for i in range(len(self.centralWidget().layout())):
      widget = self.centralWidget().layout().itemAt(i).widget()
      id = widget.property("idx")
      if id is None:
        continue

      if isinstance(widget, (RLineEdit, RTwoStateButton, RComboBox)):
        widget.UpdatePV()

    if self.hasMap:
      self.xMap.UpdatePVs()
      self.yMap.UpdatePVs()
      self.ddMap.UpdatePVs()
  
    if self.hasLink:
      for link in self.linkWidgetList:
        link.UpdatePVs()

    if self.hasDiag:
      for diag in self.diagWidgetList:
        diag.UpdatePVs()

    if self.hasFifoReset:
      self.fifoReset.UpdatePVs()

    if self.hasMTRGLink:
      for link in self.mtrglinkWidgetList:
        link.UpdatePVs()

    if self.hasVeto:
      for veto in self.vetoWidgetList:
        veto.UpdatePVs()

    if self.isRTR:
      self.rtrReg.UpdatePV()

    if self.isMTRG:
      self.mtrgReg.UpdatePV() 

  def OnChannelChanged(self, index):
    if index == 0:
      return
    ch_name = f"{self.board_name} | {self.combo_chSel.currentText()}"
    self.combo_chSel.setCurrentIndex(0)

    chIdx = index - 1
    # Show the board PVs in a new window
    if self.ch_window[chIdx]:
      self.ch_window[chIdx].raise_()
      self.ch_window[chIdx].activateWindow()
      return

    self.ch_window[chIdx] = BoardPVWindow(ch_name, self.Board, index -1, self)
    self.ch_window[chIdx].show()


  def OnRamChanged(self, index):
    if index == 0:
      return
    ram_name = f"{self.board_name} | {self.combo_ramSel.currentText()}"
    self.combo_ramSel.setCurrentIndex(0)

    ramIdx = index - 1
    # Show the RAM PVs in a new window
    if self.ram_window[ramIdx]:
      self.ram_window[ramIdx].raise_()
      self.ram_window[ramIdx].activateWindow()
      return

    self.ram_window[ramIdx] = RAMWindow(ram_name, self.ram_pvList[ramIdx], self)
    self.ram_window[ramIdx].show()