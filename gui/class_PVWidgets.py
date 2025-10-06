from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QWidget, QSpinBox, QComboBox
from PyQt6.QtCore import pyqtSignal

from class_PV import PV  # Make sure to import PV if not already
from custom_QClasses import GLineEdit, GTwoStateButton, GLabel

############################### 
class RLineEdit(GLineEdit):
  def __init__(self, pv: PV, hexBinDec = "dec", width=None, parent=None):
    super().__init__("",  parent)
    self.pv = pv
    self.hexBinDec = hexBinDec.lower()
    self.setToolTip(pv.name)

    if width is not None:
      self.setFixedWidth(width)
  
    self.returnPressed.connect(self.SetPV)
    if  pv.ReadONLY and isinstance(pv, PV)  :
      self.setReadOnly(True)
      self.setStyleSheet("color: darkgray;")

    self.isCFDfraction = False
    pvName = pv.name.split(":")[-1]
    if pvName.startswith("CFD_fraction"):
      self.isCFDfraction = True

    self.isInitialized = False

  def UnsetfixedWidth(self):
    self.setMinimumWidth(0)
    self.setMaximumWidth(1000)

  def SetPV(self):
    if isinstance(self.pv, PV):
      if self.hexBinDec == "hex":
        try:
          val = int(self.text(), 16)
        except ValueError:
          val = 0
        self.pv.SetValue(val)
      elif self.hexBinDec == "bin":
        try:
          val = int(self.text(), 2)
        except ValueError:
          val = 0
        self.pv.SetValue(val)
      else:
        self.pv.SetValue(float(self.text()))

  def UpdatePV(self, forced = False):
    if not isinstance(self.pv, PV):
      return
    if self.pv.isUpdated or forced or self.text() == "" or not self.isInitialized or self.pv.ReadONLY:
      if self.pv.value is None:
        return
      if self.hexBinDec == "hex":
        self.setText(format(int(self.pv.value) & 0xFFFFFFFF, '08X'))
      elif self.hexBinDec == "bin":
        self.setText(format(int(self.pv.value), '07b'))
      else:
        if self.isCFDfraction:
          self.setText(f"{self.pv.value:.3f}")
        else:
          self.setText(str(self.pv.value))
        
      if self.pv.ReadONLY:
        self.setStyleSheet("background-color: darkgray;")
      else:
        self.setStyleSheet("")
      self.pv.isUpdated = False
      self.isInitialized = True

#^======================================================
class RTwoStateButton(GTwoStateButton):
  def __init__(self, pv: PV, width=None, parent=None, color="green"):
    super().__init__(pv.States[0], pv.States[1], False, parent, color)
    self.pv = pv
    self.setToolTip(pv.name)
    if width is not None:
      self.setFixedWidth(width)

    self.clicked.connect(self.SetPV)
    if pv.ReadONLY:
      self.setEnabled(False)
      self.color = "darkgreen"
      self.updateAppearance()

    self.isInitialized = False

  def UnsetFixedWidth(self):
    self.setMinimumWidth(0)
    self.setMaximumWidth(1000)

  def ClearTxt(self):
    self.text1 = ""
    self.text2 = ""
    self.updateAppearance()

  def SetPV(self):
    self.pv.SetValue(int(self.state))
    self.updateAppearance()

  def UpdatePV(self, forced = False):
    if self.pv.isUpdated or forced or not self.isInitialized:
      self.setState(bool(self.pv.value))
      self.isInitialized = True

#^======================================================
class RSetButton(RTwoStateButton):
  def __init__(self, pv: PV, text, width=None, parent=None, color="lightgreen"):
    super().__init__(pv, width, parent, color)
    self.text1 = text
    self.setState(False)
  
  def SetPV(self):
    self.pv.SetValue(1)
    self.pv.SetValue(0)
    self.setState(False)

  def resetButton(self):
    self.setStyleSheet("")

#^======================================================
class RComboBox(QComboBox):
  def __init__(self, pv:PV = None, width=None, parent=None):
    super().__init__(parent)
    self.addItems(pv.States)
    self.pv = pv

    if width is not None:
      self.setFixedWidth(width)
  
    self.setToolTip(pv.name)

    self.currentIndexChanged.connect(self.on_index_changed)

    if pv.ReadONLY:
      self.setEnabled(False)

    self.isInitialized = False 

  def UnsetFixedWidth(self):
    self.setMinimumWidth(0)
    self.setMaximumWidth(1000)

  def on_index_changed(self, index):
    self.pv.SetValue(index)

  whenIndexZero = pyqtSignal(bool)
  def UpdatePV(self, forced = False):
    if self.pv.isUpdated or forced or not self.isInitialized:
      self.blockSignals(True)
      self.setCurrentIndex(int(self.pv.value))
      self.blockSignals(False)

      if int(self.pv.value) == 0:
        self.whenIndexZero.emit(True) 
      else:
        self.whenIndexZero.emit(False)
      self.setStyleSheet("")

#^======================================================
class RMapTwoStateButton(QWidget):
  def __init__(self, pvList, rows=10, cols=8, 
               customRowLabel = None, rowLabelLen=140, clearText = True,
               hasRowLabel = True, hasColLabel = True, parent=None):
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
        if cols <= len(labName):
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
      # find the length of the longest row label

    for i in range(rows):
      rowIdx += 1
      row_buttons = []

      if hasRowLabel:      
        if customRowLabel is not None:
          lbl = GLabel(customRowLabel + "  ") 
          lbl.setFixedWidth(rowLabelLen)
          lbl.setFixedHeight(20)
          layout.addWidget(lbl, rowIdx, 0)
        else:
          lbl = QLabel(str(i)) 
          lbl.setFixedWidth(20)
          lbl.setFixedHeight(20)
          layout.addWidget(lbl, rowIdx, 0)

      for j in range(cols):
        btn = RTwoStateButton(pvList[j * rows + i], None, self, color="green")
        if clearText:
          btn.ClearTxt()
          btn.setFixedWidth(20)
        else:
          btn.setFixedWidth(80)
        btn.setFixedHeight(20)
        if hasRowLabel:
          layout.addWidget(btn, rowIdx, j+1)
        else: 
          layout.addWidget(btn, rowIdx, jm)
        row_buttons.append(btn)
      self.buttons.append(row_buttons)

  def UpdatePV(self, forced = True): # i know it is PVsssssss, but for consistency, drop the s
    for i in range(self.rows):
      for j in range(self.cols):
        self.buttons[i][j].UpdatePV(forced)

  def SetInvertStateColor(self, isInvert: bool):
    for i in range(self.rows):
      for j in range(self.cols):
        self.buttons[i][j].SetInvertStateColor(isInvert)

#^======================================================
class RMapLineEdit(QWidget):
  def __init__(self, pvList, rows=10, cols=8, customRowLabel = None, hasRowLabel = True, hasColLabel = True,  parent=None):
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
    if hasColLabel :
      for j in range(cols):
        lbl = GLabel(chr(ord('A') + j)) 
        lbl.setFixedWidth(30)
        lbl.setFixedHeight(20)
        layout.addWidget(lbl, rowIdx, j+1)
    else:
      rowIdx = -1

    if customRowLabel is not None:
      hasRowLabel = True

    for i in range(rows):
      rowIdx += 1
      row_lineedits = []

      if hasRowLabel:
        if customRowLabel is not None:
          lbl = GLabel(customRowLabel + "  ") 
          lbl.setFixedWidth(140)
          lbl.setFixedHeight(20)
          layout.addWidget(lbl, rowIdx, 0)
        else:
          lbl = GLabel(str(i)) 
          lbl.setFixedWidth(20)
          lbl.setFixedHeight(20)
          layout.addWidget(lbl, rowIdx, 0)

      for j in range(cols):
        le = RLineEdit(pvList[j * rows + i], width=None, parent=self)
        le.setFixedWidth(40)
        le.setFixedHeight(20)
        if hasRowLabel:
          layout.addWidget(le, rowIdx, j+1)
        else:
          layout.addWidget(le, rowIdx, j)
        row_lineedits.append(le)
      self.lineedits.append(row_lineedits)

  def UpdatePV(self, forced = True): # i know it is PVsssssss, but for consistency, drop the s
    for i in range(self.rows):
      for j in range(self.cols):
        self.lineedits[i][j].UpdatePV(forced)

#^======================================================
class RRegisterDisplay(QWidget):
  def __init__(self, pv: PV, isRTR: bool, showRowLabel=True, parent=None):
    super().__init__(parent)
    layout = QGridLayout(self)
    layout.setVerticalSpacing(2)  # Remove vertical gaps between rows
    layout.setHorizontalSpacing(2)  # Optional: small horizontal gap
    layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    self.pv = pv

    items = ["NIM in B", "NIM in A", "R Lock", "Fast Str", "CPLD 1", "CPLD 2", "CPLD 4", "CPLD 8", "L init State 1", "L init State 2", "L init State 4", "L init State 8", "0", "0", "All Lock", "Lock Err"]
    if not isRTR:
      items = ["NIM in B", "NIM in A", "TS roll", "Fast Str", "rsvd", "rsvd", "rsvd", "rsvd", "L init State 1", "L init State 2", "L init State 4", "L init State 8", "Trig Veto", "0", "All Lock", "Lock Err"]

    self.btnList = []

    row = 0
    for i, name in enumerate(items):
      if showRowLabel:
        layout.addWidget(GLabel(name + "  ", alignment=Qt.AlignmentFlag.AlignRight), row, 0)

      btn = GTwoStateButton("", "", color="darkgreen")
      btn.setFixedWidth(20)
      btn.setFixedHeight(20)
      btn.setEnabled(False)
      self.btnList.append(btn)
      layout.addWidget(btn, row, 1)

      row += 1

  def UpdatePV(self, forced = True):
    if self.pv.isUpdated or forced:
      val = int(self.pv.value)
      for i in range(16):
        state = (val >> i) & 0x1
        self.btnList[i].setState(state)
