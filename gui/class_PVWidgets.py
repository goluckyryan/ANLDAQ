from custom_QClasses import GLineEdit, GTwoStateButton, GLabel, GMapTwoStateButton, GMapSpinBox

from PyQt6.QtWidgets import QLabel, QLineEdit, QGridLayout, QPushButton, QWidget, QSpinBox, QComboBox

from class_PV import PV  # Make sure to import PV if not already

############################### 
class RLineEdit(GLineEdit):
  def __init__(self, pv: PV, parent=None):
    super().__init__("",  parent)
    self.pv = pv
    self.setToolTip(pv.name)
    if  pv.ReadONLY:
      self.setReadOnly(True)
      self.setStyleSheet("color: darkgray;")

    self.returnPressed.connect(self.SetPV)

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
    super().__init__(pv.States[0], pv.States[1], parent, color)
    self.pv = pv
    self.setToolTip(pv.name)
    if pv.ReadONLY:
      self.setEnabled(False)
      self.updateAppearance()

    self.clicked.connect(self.SetPV)

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
    self.currentIndexChanged.connect(self.on_index_changed)

    self.setToolTip(pv.name)

    if pv.ReadONLY:
      self.setEnabled(False)

    self.enableSignal = True
    self.on_index_changed(self.currentIndex())

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