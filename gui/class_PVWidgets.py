from custom_QClasses import GLineEdit, GTwoStateButton, GLabel
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QWidget, QSpinBox, QComboBox

from class_PV import PV  # Make sure to import PV if not already

############################### 
class RLineEdit(GLineEdit):
  def __init__(self, pv: PV, parent=None):
    super().__init__("",  parent)
    self.pv = pv
    self.setToolTip(pv.name)

    self.returnPressed.connect(self.SetPV)
    if  pv.ReadONLY:
      self.setReadOnly(True)
      self.setStyleSheet("color: darkgray;")


  def SetPV(self):
    if isinstance(self.pv, PV):
      self.pv.SetValue(float(self.text()))

  def UpdatePV(self):
    if self.pv.isUpdated:
      self.setText(str(self.pv.value))
      if self.pv.ReadONLY:
        self.setStyleSheet("background-color: darkgray;")
      else:
        self.setStyleSheet("")


class RTwoStateButton(GTwoStateButton):
  def __init__(self, pv: PV, parent=None, color="green"):
    super().__init__(pv.States[0], pv.States[1], False, parent, color)
    self.pv = pv
    self.setToolTip(pv.name)

    self.clicked.connect(self.SetPV)
    if pv.ReadONLY:
      self.setEnabled(False)
      self.color = "darkgreen"
      self.updateAppearance()

  def ClearTxt(self):
    self.text1 = ""
    self.text2 = ""
    self.updateAppearance()

  def SetPV(self):
    self.pv.SetValue(int(self.state))
    self.updateAppearance()

  def UpdatePV(self):
    if self.pv.isUpdated:
      self.setState(bool(self.pv.value))


class RComboBox(QComboBox):
  def __init__(self, pv:PV = None, parent=None):
    super().__init__(parent)
    self.addItems(pv.States)
    self.pv = pv

    self.setToolTip(pv.name)
    self.enableSignal = False
    self.on_index_changed(self.currentIndex())

    if pv.ReadONLY:
      self.setEnabled(False)

  def on_index_changed(self, index):
    if not self.enableSignal:
      return
    self.pv.SetValue(index)

  def UpdatePV(self):
    if self.pv.isUpdated:
      self.enableSignal = False
      self.setCurrentIndex(int(self.pv.value))
      self.setStyleSheet("")
      self.enableSignal = True


class RMapTwoStateButton(QWidget):
  def __init__(self, pvList, rows=10, cols=8, customRowLabel = None, hasRowLabel = True, hasColLabel = True, parent=None):
    super().__init__(parent)
    self.rows = rows
    self.cols = cols
    self.buttons = []
    self.pvList = pvList

    layout = QGridLayout(self)
    layout.setVerticalSpacing(2)  # Remove vertical gaps between rows
    layout.setHorizontalSpacing(2)  # Optional: small horizontal gap
    layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    labName = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'L', 'R', 'U']

    if hasColLabel :
      rowIdx = 0
      for j in range(cols):
        if cols < len(labName):
          lbl = GLabel(labName[j])
        else:
          # lbl = GLabel(chr(ord('A') + j)) 
          lbl = GLabel(str(j))

        lbl.setFixedWidth(20)
        lbl.setFixedHeight(20)
        if hasRowLabel:
          layout.addWidget(lbl, rowIdx, j+1)
        else:
          layout.addWidget(lbl, rowIdx, j)
    else:
      rowIdx = -1

    if customRowLabel is not None:
      # for pv in pvList:
      #   print(f"Array PV: {pv.name}")
      hasRowLabel = True

    for i in range(rows):
      rowIdx += 1
      row_buttons = []

      if hasRowLabel:      
        if customRowLabel is not None:
          lbl = QLabel(customRowLabel) 
          lbl.setFixedWidth(120)
          lbl.setFixedHeight(20)
          layout.addWidget(lbl, rowIdx, 0)
        else:
          lbl = QLabel(str(i)) 
          lbl.setFixedWidth(20)
          lbl.setFixedHeight(20)
          layout.addWidget(lbl, rowIdx, 0)

      for j in range(cols):
        btn = RTwoStateButton(pvList[j * rows + i], self, color="green")
        btn.ClearTxt()
        btn.setFixedWidth(20)
        btn.setFixedHeight(20)
        if hasRowLabel:
          layout.addWidget(btn, rowIdx, j+1)
        else: 
          layout.addWidget(btn, rowIdx, j)
        row_buttons.append(btn)
      self.buttons.append(row_buttons)

  def UpdatePVs(self):
    for i in range(self.rows):
      for j in range(self.cols):
        self.buttons[i][j].UpdatePV()

  def SetInvertStateColor(self, isInvert: bool):
    for i in range(self.rows):
      for j in range(self.cols):
        self.buttons[i][j].SetInvertStateColor(isInvert)


class RMapLineEdit(QWidget):
  def __init__(self, pvList, rows=10, cols=8,  parent=None):
    super().__init__(parent)
    self.rows = rows
    self.cols = cols
    self.lineedits = []
    self.pvList = pvList

    layout = QGridLayout(self)
    layout.setVerticalSpacing(2)  # Remove vertical gaps between rows
    layout.setHorizontalSpacing(2)  # Optional: small horizontal gap
    layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    rowIdx = 0
    for j in range(cols):
      lbl = GLabel(chr(ord('A') + j)) 
      lbl.setFixedWidth(30)
      lbl.setFixedHeight(20)
      layout.addWidget(lbl, rowIdx, j+1)

    for i in range(rows):
      rowIdx += 1
      row_lineedits = []
      lbl = GLabel(str(i)) 
      lbl.setFixedWidth(20)
      lbl.setFixedHeight(20)
      layout.addWidget(lbl, rowIdx, 0)
      for j in range(cols):
        le = RLineEdit(pvList[j * rows + i], self)
        le.setFixedWidth(40)
        le.setFixedHeight(20)
        layout.addWidget(le, rowIdx, j+1)
        row_lineedits.append(le)
      self.lineedits.append(row_lineedits)

  def UpdatePVs(self):
    for i in range(self.rows):
      for j in range(self.cols):
        self.lineedits[i][j].UpdatePV()