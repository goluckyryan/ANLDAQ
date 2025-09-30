
from PyQt6.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QWidget, QSpinBox, QComboBox
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPainter, QPen, QPolygon

from class_PV import PV
import math


#make a new GLabel class that inherits from QLabel, and always has right alignment
class GLabel(QLabel):
  def __init__(self, text, alignment = Qt.AlignmentFlag.AlignRight, parent=None):
    super().__init__(text)
    self.setAlignment(alignment | Qt.AlignmentFlag.AlignVCenter)

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

  def SetText1(self, text):
    self.text1 = text
    self.updateAppearance()

  def SetText2(self, text):
    self.text2 = text
    self.updateAppearance()

  def SetTexts(self, text1, text2):
    self.text1 = text1
    self.text2 = text2
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

  stateChanged = pyqtSignal(bool)

  def setState(self, state: bool):
    self.state = state
    self.stateChanged.emit(self.state)
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


class GArrow(QWidget):
  def __init__(self, length=50, color=Qt.GlobalColor.black, angle=0, parent=None):
    super().__init__(parent)
    self.length = length
    self.color = color
    self.angle = angle  # angle in degrees
    self.setMinimumSize(self.length + 30, 40)

  def setLength(self, length):
    self.length = length
    self.setMinimumSize(self.length + 30, 40)
    self.update()

  def setColor(self, color):
    self.color = color
    self.update()

  def setAngle(self, angle):
    self.angle = angle
    self.update()

  def paintEvent(self, event):
    painter = QPainter(self)
    pen = QPen(self.color, 2)
    painter.setPen(pen)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    # Center the arrow in the widget
    center_x = self.width() // 2
    center_y = self.height() // 2

    # Calculate start and end points based on angle
    rad = math.radians(self.angle)
    dx = math.cos(rad) * self.length / 2
    dy = math.sin(rad) * self.length / 2

    start_x = center_x - dx
    start_y = center_y - dy
    end_x = center_x + dx
    end_y = center_y + dy

    painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))

    # Arrow head
    arrow_size = 10
    angle_offset = math.radians(30)  # 30 degrees for arrow head

    # Calculate arrow head points
    arrow_pnt = QPoint(int(end_x), int(end_y))
    left_angle = rad - angle_offset
    right_angle = rad + angle_offset

    left_pnt = QPoint(
      int(end_x - arrow_size * math.cos(left_angle)),
      int(end_y - arrow_size * math.sin(left_angle))
    )
    right_pnt = QPoint(
      int(end_x - arrow_size * math.cos(right_angle)),
      int(end_y - arrow_size * math.sin(right_angle))
    )

    arrow_head = QPolygon([arrow_pnt, left_pnt, right_pnt])
    painter.setBrush(self.color)
    painter.drawPolygon(arrow_head)