from PyQt6.QtWidgets import QMainWindow, QGridLayout, QComboBox, QWidget

from class_DIG import DIG

from custom_QClasses import GLineEdit, GTwoStateButton, GLabel
from PyQt6.QtCore import QTimer

class BoardPVWindow(QMainWindow):
  def __init__(self, board_name,  board : DIG, parent=None):
    super().__init__(parent)
    self.setWindowTitle(f"Board PVs: {board_name}")
    self.setGeometry(150, 150, 300, 400)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #=============================== GUI setup
    rowIndex = 0
    colIndex = 0

    for i, pv in enumerate(board.Board_PV):
      pvName = pv.name.split(":")[-1]
      layout.addWidget(GLabel(f"{pvName}"), rowIndex, colIndex)
      if pv.NumStates() == 2:
        btn = GTwoStateButton(pv.States[0], pv.States[1], color="green")
        btn.setProperty("idx", i)
        btn.setToolTip(pv.name)
        # if pv.Type == "OUT":
        #   btn.setEnabled(False)
        # btn.clicked.connect(lambda checked, pv=pv, btn=btn: self.SetPV(pv, btn))
        layout.addWidget(btn, rowIndex, colIndex + 1)

      elif pv.NumStates() > 2: #use QComboBox
        layout.addWidget(GLabel(f"{pvName}"), rowIndex, colIndex)
        combo = QComboBox()
        combo.setProperty("idx", i)
        combo.setToolTip(pv.name)
        combo.addItems(pv.States)
        # if pv.Type == "OUT":
        #   combo.setEnabled(False)
        # combo.currentIndexChanged.connect(lambda index, pv=pv, combo=combo: self.SetPV(pv, combo))
        layout.addWidget(combo, rowIndex, colIndex + 1)

      else:

        layout.addWidget(GLabel(f"{pvName}"), rowIndex, colIndex)
        le = GLineEdit("")
        le.setToolTip(pv.name)
        le.setProperty("idx", i)
        # if pv.Type == "OUT":
        #   le.setReadOnly(True)
        #   le.setStyleSheet("background-color: lightgray;")
        le.setText(str(pv.value))
        layout.addWidget(le, rowIndex, colIndex + 1)

      rowIndex += 1
      if rowIndex >= 20:
        rowIndex = 0
        colIndex += 2
      

    #=============================== End of GUI setup

    self.Board = board

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

      # pv_name = widget.toolTip()
      # if "live_timestamp_lsb" in pv_name.lower():
      #   pv = self.Board.Board_PV[id]
      #   print(f"Checking PV {pv.name}({pv_name}), isUpdated={pv.isUpdated} | {pv.value}, {pv.char_value}")

      #   widget.setText(str(pv.value))
      #   widget.setStyleSheet("")
      # else:
      #   continue

      pv = self.Board.Board_PV[id]

      if pv.isUpdated:
        print(f"Checking PV {pv.name}, isUpdated={pv.isUpdated}")
        value = pv.char_value
        pv.isUpdated = False

        if isinstance(widget, GLineEdit):
          widget.setText(str(value))
          widget.setStyleSheet("") 
        elif isinstance(widget, GTwoStateButton):
          if value == pv.States[0]:
            widget.setChecked(False)
          elif value == pv.States[1]:
            widget.setChecked(True)
        elif isinstance(widget, QComboBox):
          if value in pv.States:
            index = pv.States.index(value)
            widget.setCurrentIndex(index)
          widget.setStyleSheet("") 
      