
from PyQt6.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QWidget, QSpinBox, QComboBox
from PyQt6.QtCore import Qt

from class_PV import PV

#make a new GLabel class that inherits from QLabel, and always has right alignment
class GLabel(QLabel):
  def __init__(self, text, vAlign = Qt.AlignmentFlag.AlignVCenter, parent=None):
    super().__init__(text)
    self.setAlignment(Qt.AlignmentFlag.AlignRight | vAlign)

#make a new GLineEdit class that inherits from QLineEdit. when text changed, set text color to be blue, when enter pressed, set text color to be black
class GLineEdit(QLineEdit):
  def __init__(self, text, parent=None):
    super().__init__(text, parent)
    self.textChanged.connect(self.on_text_changed)
    self.returnPressed.connect(self.on_return_pressed)

  def on_text_changed(self):
    self.setStyleSheet("color: blue")

  def on_return_pressed(self):
    self.setStyleSheet("")

#create a class of GTwoStateButton, it has two states, when clicked, it toggles between the two states
class GTwoStateButton(QPushButton):
  def __init__(self, text1, text2, isInvert = False, parent=None, color="lightgreen"):
    super().__init__(text1, parent)
    self.text1 = text1
    self.text2 = text2
    self.state = False
    self.clicked.connect(self.toggleState)
    self.isInvertStateColor = isInvert
    self.color = color
    self.disable_font_color = "brown"
    self.updateAppearance()

  def toggleState(self):
    self.state = not self.state
    self.updateAppearance()

  def SetInvertStateColor(self, isInvert: bool):
    self.isInvertStateColor = isInvert
    self.updateAppearance()

  def updateAppearance(self):
    if self.state:
      self.setText(self.text2)

      if self.isEnabled():

        if self.isInvertStateColor:
          self.setStyleSheet("")
        else:
          self.setStyleSheet(f"background-color: {self.color}")
      else:
        if self.isInvertStateColor:
          self.setStyleSheet(f"color: {self.disable_font_color};")
        else:
          self.setStyleSheet(f"color: {self.disable_font_color}; background-color: {self.color}")
    else:

      self.setText(self.text1)
  
      if self.isEnabled():
        if self.isInvertStateColor:
          self.setStyleSheet(f"background-color: {self.color}")
        else:
          self.setStyleSheet("")
      else:
        if self.isInvertStateColor:
          self.setStyleSheet(f"color: {self.disable_font_color}; background-color: {self.color}")
        else:
          self.setStyleSheet(f"color: {self.disable_font_color};")

  def setState(self, state: bool):
    self.state = state
    self.updateAppearance()



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

