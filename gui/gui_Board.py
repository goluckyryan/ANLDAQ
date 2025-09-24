from PyQt6.QtWidgets import QMainWindow, QGridLayout, QComboBox, QWidget, QGroupBox
from PyQt6.QtWidgets import QApplication

from class_Board import Board
from class_PV import PV  # Make sure to import PV if not already

from custom_QClasses import GLineEdit, GTwoStateButton, GLabel, GMapButton
from PyQt6.QtCore import QTimer

class BoardPVWindow(QMainWindow):
  def __init__(self, board_name,  board : Board, channelNo = -1, parent=None):
    super().__init__(parent)
    self.board_name = board_name
    self.channelNo = channelNo
    self.Board = board

    self.setWindowTitle(f"{board_name}")
    self.setGeometry(150, 150, 300, 400)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #=============================== GUI setup
    rowIndex = 0
    colIndex = 0
    maxRows = 20

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

    array_pv = ["DEN_", "GATED_THROTTLE", "LINK_", "Diag_", "LOCK_", "RAW_THROTTLE", "REN_", "RPwr_", "SLiL_", "SLoL_", "SYNC_", "TPwr_", "FIFOReset", "ILM", "LED", "LRUCtl" ]
    self.hasArray = False

    for i, pv in enumerate(pv_list):
      if not isinstance(pv, PV):
        continue
      pvName = pv.name.split(":")[-1]

      if any(pvName.startswith(prefix) for prefix in map_pv):
        if not self.hasMap:
          self.hasMap = True
        continue

      if any(pvName.startswith(prefix) for prefix in array_pv):
        if not self.hasArray:
          self.hasArray = True
        continue

      layout.addWidget(GLabel(f"{pvName}"), rowIndex, colIndex)
      if pv.NumStates() == 2:
        btn = GTwoStateButton(pv.States[0], pv.States[1])
        btn.setProperty("idx", i)
        btn.setToolTip(pv.name)
        if pv.ReadONLY:
          btn.setEnabled(False)
        btn.clicked.connect(lambda checked, pv=pv, btn=btn: self.SetPV(pv, btn))
        layout.addWidget(btn, rowIndex, colIndex + 1)

      elif pv.NumStates() > 2: #use QComboBox
        combo = QComboBox()
        combo.setProperty("idx", i)
        combo.setToolTip(pv.name)
        combo.addItems(pv.States)
        if pv.ReadONLY:
          combo.setEnabled(False)
        combo.currentIndexChanged.connect(lambda index, pv=pv, combo=combo: self.SetPV(pv, combo))
        layout.addWidget(combo, rowIndex, colIndex + 1)

      else:
        le = GLineEdit("")
        le.setToolTip(pv.name)
        le.setProperty("idx", i)
        if pv.ReadONLY:
          le.setReadOnly(True)
          le.setStyleSheet("background-color: lightgray;")
        le.setText(str(pv.value))
        le.returnPressed.connect(lambda pv=pv, le=le: self.SetPV(pv, le))
        layout.addWidget(le, rowIndex, colIndex + 1)

      rowIndex += 1
      if rowIndex >= maxRows:
        rowIndex = 0
        colIndex += 2
      

    rowIndex = 0
    colIndex += 2
    if self.hasMap:
      groupBox_map = QGroupBox("Mapping")
      map_layout = QGridLayout()
      groupBox_map.setLayout(map_layout)
      layout.addWidget(groupBox_map, rowIndex, colIndex, maxRows, 8 )

      map_layout.addWidget(GLabel("X Map:"), 0, 0)
      self.xMap = GMapButton(parent=self)
      map_layout.addWidget(self.xMap, 0, 1)

      self.yMap = GMapButton(parent=self)
      map_layout.addWidget(GLabel("Y Map:"), 1, 0)
      map_layout.addWidget(self.yMap, 1, 1)

    # Set focus to none after GUI setup
    QApplication.focusWidget().clearFocus()

    #=============================== End of GUI setup

    self.ch_window = [[] for _ in range(board.NumChannels)]

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

      if self.channelNo >= 0 and self.Board.NumChannels > 0:
        pv = self.Board.CH_PV[self.channelNo][id]
      else:
        pv = self.Board.Board_PV[id]

      if not isinstance(pv, PV):
        continue

      if pv.isUpdated:
        # print(f"Checking PV {pv.name} = {pv.value}, isUpdated={pv.isUpdated}")
        value = pv.value
        pv.isUpdated = False

        self.EnableConnect = False

        if isinstance(widget, GLineEdit):
          widget.setText(str(value))
          widget.setStyleSheet("")
          if pv.ReadONLY:
            widget.setStyleSheet("background-color: lightgray;")
        elif isinstance(widget, GTwoStateButton):
          widget.setState(value)
        elif isinstance(widget, QComboBox):
          widget.setCurrentIndex(value)
          widget.setStyleSheet("") 

        self.EnableConnect = True
  
  def SetPV(self, pv, widget):
    if not self.EnableConnect:
      return
    if isinstance(widget, GTwoStateButton):
      pv.SetValue(int(widget.state))
    elif isinstance(widget, QComboBox):
      pv.SetValue(int(widget.currentIndex()))
    elif isinstance(widget, GLineEdit):
      text = widget.text()
      try:
        val = float(text)
        if val.is_integer():
          val = int(val)
        pv.SetValue(val)
        widget.setStyleSheet("") 
      except ValueError:
        widget.setStyleSheet("background-color: red;") 
        return

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