
from PyQt6.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QWidget, QSpinBox
from PyQt6.QtCore import Qt

from class_PV import PV

#make a new GLabel class that inherits from QLabel, and always has right alignment
class GLabel(QLabel):
  def __init__(self, text):
    super().__init__(text)
    self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

#make a new GLineEdit class that inherits from QLineEdit. when text changed, set text color to be blue, when enter pressed, set text color to be black
class GLineEdit(QLineEdit):
  def __init__(self, text):
    super().__init__(text)
    self.textChanged.connect(self.on_text_changed)
    self.returnPressed.connect(self.on_return_pressed)

  def on_text_changed(self):
    self.setStyleSheet("color: blue")

  def on_return_pressed(self):
    self.setStyleSheet("color: black")


#create a class for flag display, it has GLabel and Qpushbutton (disabled), if the flag is set, the button turns green
#when mouse hovers over the button, display a tooltip message based on the flag state
class GFlagDisplay(QWidget):
  def __init__(self, label_text, fail_msg="", true_msg="", parent=None):
    super().__init__(parent)
    layout = QGridLayout(self)
    layout.setVerticalSpacing(0)  # Remove vertical gaps between rows
    layout.setHorizontalSpacing(4)  # Optional: small horizontal gap
    layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
    
    self.label = GLabel(label_text)
    self.label.setFixedWidth(200)
    self.label.setFixedHeight(20)

    self.button = QPushButton()
    self.button.setEnabled(False)
    self.button.setFixedWidth(20)
    self.button.setFixedHeight(20)

    layout.addWidget(self.label, 0, 0)
    layout.addWidget(self.button, 0, 1)

    self.true_msg = true_msg
    self.fail_msg = fail_msg
    self.flag = False

    self.button.setToolTip(self.fail_msg)

  def setFlag(self, flag: bool):
    self.flag = flag
    if flag:
      self.button.setStyleSheet("background-color: green")
      self.button.setToolTip(self.true_msg)
    else:
      self.button.setStyleSheet("")
      self.button.setToolTip(self.fail_msg)


#create a class of GTwoStateButton, it has two states, when clicked, it toggles between the two states
class GTwoStateButton(QPushButton):
  def __init__(self, text1, text2, parent=None, color="green"):
    super().__init__(text1, parent)
    self.text1 = text1
    self.text2 = text2
    self.state = False
    self.clicked.connect(self.toggleState)
    self.updateAppearance()
    self.color = color

  def toggleState(self):
    self.state = not self.state
    self.updateAppearance()

  def updateAppearance(self):
    if self.state:
      self.setText(self.text2)
      if self.isEnabled():
        self.setStyleSheet(f"background-color: {self.color}")
      else:
        self.setStyleSheet(f"color: darkgray; background-color: {self.color}")
    else:
      self.setText(self.text1)
      if self.isEnabled():
        self.setStyleSheet("")
      else:
        self.setStyleSheet("color: darkgray;")

  def setState(self, state: bool):
    self.state = state
    self.updateAppearance()
  
#creaet a class of GArray that can be any widget.
class GArray(QWidget):
  def __init__(self, widget_class, rows=10, cols=8, parent=None):
    super().__init__(parent)
    self.rows = rows
    self.cols = cols
    self.widgets = []

    layout = QGridLayout(self)
    layout.setVerticalSpacing(2)  # Remove vertical gaps between rows
    layout.setHorizontalSpacing(2)  # Optional: small horizontal gap
    layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    for i in range(rows):
      row_widgets = []
      for j in range(cols):
        widget = widget_class()
        widget.setFixedWidth(40)
        widget.setFixedHeight(20)
        layout.addWidget(widget, i, j)
        row_widgets.append(widget)
      self.widgets.append(row_widgets)

  def getWidget(self, row: int, col: int):
    if 0 <= row < self.rows and 0 <= col < self.cols:
      return self.widgets[row][col]
    return None

#create a class of GMapButton, it has 10 rows and 8 columns of buttons. Each Buttons has two states, when clicked, it toggles between the two states
class GMapTwoStateButton(QWidget):
  def __init__(self, pvList, rows=10, cols=8,  parent=None):
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

    rowIdx = 0
    for j in range(cols):
      lbl = GLabel(chr(ord('A') + j)) 
      lbl.setFixedWidth(20)
      lbl.setFixedHeight(20)
      layout.addWidget(lbl, rowIdx, j+1)

    for i in range(rows):
      rowIdx += 1
      row_buttons = []
      lbl = GLabel(str(i)) 
      lbl.setFixedWidth(20)
      lbl.setFixedHeight(20)
      layout.addWidget(lbl, rowIdx, 0)
      for j in range(cols):
        btn = GTwoStateButton("", "", self, color="green")
        btn.setFixedWidth(20)
        btn.setFixedHeight(20)
        btn.setProperty("id", j * rows + i)  # column-major order
        btn.clicked.connect(self.onButtonClicked)
        layout.addWidget(btn, rowIdx, j+1)
        row_buttons.append(btn)
      self.buttons.append(row_buttons)

  def setButtonState(self, row: int, col: int, state: bool):
    if 0 <= row < self.rows and 0 <= col < self.cols:
      self.buttons[row][col].setState(state)

  def getButtonState(self, row: int, col: int) -> bool:
    if 0 <= row < self.rows and 0 <= col < self.cols:
      return self.buttons[row][col].state
    return False

  def onButtonClicked(self):
    btn = self.sender()
    id = btn.property("id")
    state = btn.state
    pv = self.pvList[id]
    if isinstance(pv, PV):
      pv.SetValue(int(state))


  def UpdatePVs(self):
    for i in range(self.rows):
      for j in range(self.cols):
        idx = j * self.rows + i
        if idx < len(self.pvList):
          pv = self.pvList[idx]
          if isinstance(pv, PV) and  pv.isUpdated:
            state = bool(pv.value)
            self.setButtonState(i, j, state)

class GMapSpinBox(QWidget):
  def __init__(self, pvList, rows=10, cols=8,  parent=None):
    super().__init__(parent)
    self.rows = rows
    self.cols = cols
    self.spinboxes = []
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
      row_spinboxes = []
      lbl = GLabel(str(i)) 
      lbl.setFixedWidth(20)
      lbl.setFixedHeight(20)
      layout.addWidget(lbl, rowIdx, 0)
      for j in range(cols):
        spb = QSpinBox(self)
        spb.setFixedWidth(40)
        spb.setFixedHeight(20)
        spb.setRange(0, 255)
        spb.setProperty("id", j * rows + i)  # column-major order
        spb.valueChanged.connect(self.onSpinBoxValueChanged)
        layout.addWidget(spb, rowIdx, j+1)
        row_spinboxes.append(spb)
      self.spinboxes.append(row_spinboxes)

  def setSpinBoxValue(self, row: int, col: int, value: int):
    if 0 <= row < self.rows and 0 <= col < self.cols:
      self.spinboxes[row][col].setValue(value)

  def getSpinBoxValue(self, row: int, col: int) -> int:
    if 0 <= row < self.rows and 0 <= col < self.cols:
      return self.spinboxes[row][col].value()
    return 0

  def onSpinBoxValueChanged(self):
    spb = self.sender()
    id = spb.property("id")
    value = int(spb.value())
    pv = self.pvList[id]
    if isinstance(pv, PV):
      pv.SetValue(value)

  def UpdatePVs(self):
    for i in range(self.rows):
      for j in range(self.cols):
        idx = j * self.rows + i
        if idx < len(self.pvList):
          pv = self.pvList[idx]
          if isinstance(pv, PV) and  pv.isUpdated:
            value = int(pv.value)
            self.setSpinBoxValue(i, j, value)
