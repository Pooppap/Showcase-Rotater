from msilib.schema import Class
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from utils import VideoQThread


class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.showFullScreen()
        
        menu_bar = self.menuBar()
        
        
        self.main_frame = QtGui.QLabel()
        