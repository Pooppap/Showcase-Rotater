from PyQt5 import QtGui
from PyQt5 import QtCore


class CallbackSignal(QtCore.QObject):
    frame_signal = QtCore.pyqtSignal(QtGui.QImage)