
from PyQt6.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QWidget
from PyQt6.QtCore import Qt

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