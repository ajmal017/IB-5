from GUI.main_gui import Mainwindow
from PyQt5 import QtWidgets
import sys
import qdarkstyle



app = QtWidgets.QApplication([])
application = Mainwindow()
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
application.show()
sys.exit(app.exec())