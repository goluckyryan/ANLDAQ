from PyQt6.QtWidgets import QMainWindow, QGridLayout, QComboBox, QWidget

from class_Board import Board

from custom_QClasses import GLineEdit, GTwoStateButton, GLabel
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
    
    for i, pv in enumerate(pv_list):
      pvName = pv.name.split(":")[-1]
      layout.addWidget(GLabel(f"{pvName}"), rowIndex, colIndex)
      if pv.NumStates() == 2:
        btn = GTwoStateButton(pv.States[0], pv.States[1], color="green")
        btn.setProperty("idx", i)
        btn.setToolTip(pv.name)
        # if pv.Type == "OUT":
        #   btn.setEnabled(False)
        btn.clicked.connect(lambda checked, pv=pv, btn=btn: self.SetPV(pv, btn))
        layout.addWidget(btn, rowIndex, colIndex + 1)

      elif pv.NumStates() > 2: #use QComboBox
        layout.addWidget(GLabel(f"{pvName}"), rowIndex, colIndex)
        combo = QComboBox()
        combo.setProperty("idx", i)
        combo.setToolTip(pv.name)
        combo.addItems(pv.States)
        # if pv.Type == "OUT":
        #   combo.setEnabled(False)
        combo.currentIndexChanged.connect(lambda index, pv=pv, combo=combo: self.SetPV(pv, combo))
        layout.addWidget(combo, rowIndex, colIndex + 1)

      else:

        layout.addWidget(GLabel(f"{pvName}"), rowIndex, colIndex)
        le = GLineEdit("")
        le.setToolTip(pv.name)
        le.setProperty("idx", i)
        # if pv.Type == "OUT":
        #   le.setReadOnly(True)
          # le.setStyleSheet("background-color: lightgray;")
        le.setText(str(pv.value))
        le.returnPressed.connect(lambda pv=pv, le=le: self.SetPV(pv, le))
        layout.addWidget(le, rowIndex, colIndex + 1)

      rowIndex += 1
      if rowIndex >= 20:
        rowIndex = 0
        colIndex += 2
      

    #=============================== End of GUI setup

    self.ch_window = [[] for _ in range(board.NumChannels)]

    self.timer = QTimer(self)
    self.timer.setInterval(500)  # check every 500 ms
    self.timer.timeout.connect(self.update_pvs)
    self.timer.start()

  def closeEvent(self, event):
    self.timer.stop()
    super().closeEvent(event)

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

      if pv.isUpdated:
        # print(f"Checking PV {pv.name} = {pv.value}, isUpdated={pv.isUpdated}")
        value = pv.value
        pv.isUpdated = False

        if isinstance(widget, GLineEdit):
          widget.setText(str(value))
          widget.setStyleSheet("") 
        elif isinstance(widget, GTwoStateButton):
            widget.setState(value)
        elif isinstance(widget, QComboBox):
          widget.setCurrentIndex(value)
          widget.setStyleSheet("") 
  
  def SetPV(self, pv, widget):
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