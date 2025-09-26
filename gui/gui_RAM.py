from class_PVWidgets import  RMapTwoStateButton
from PyQt6.QtWidgets import QMainWindow, QGridLayout, QComboBox, QWidget, QGroupBox, QLabel
from PyQt6.QtCore import QTimer, Qt


class RAMWindow(QMainWindow):
  def __init__(self, ram_name,  pvList, parent=None):
    super().__init__(parent)
    self.board_name = ram_name
    self.pvList = pvList

    self.setWindowTitle(f"{ram_name} RAM")
    self.setGeometry(150, 150, 300, 400)

    central_widget = QWidget()
    self.setCentralWidget(central_widget)

    layout = QGridLayout()
    central_widget.setLayout(layout)

    #=============================== GUI setup
    self.mapTable = RMapTwoStateButton(pvList = self.pvList, rows=32, cols=32, parent=self)
    layout.addWidget(self.mapTable, 0, 0)


    self.timer = QTimer(self)
    self.timer.timeout.connect(self.OnTimer)
    self.timer.start(500)  # Update every second

  def OnTimer(self):
    self.mapTable.UpdatePVs()