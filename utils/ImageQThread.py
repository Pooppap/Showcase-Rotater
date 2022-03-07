import cv2
import numpy as np

from time import sleep
from PyQt5 import QtGui
from PyQt5 import QtCore
from pdf2image import convert_from_path


class ImageQThread(QtCore.QObject):
    frame_signal = QtCore.pyqtSignal(QtGui.QImage)
    done_signal = QtCore.pyqtSignal()
    
    def __init__(self, image_file, frame_size, default_delay=30.0):
        super().__init__()
        self.__image_file = image_file
        self.__frame_size = frame_size
        self.__default_delay = default_delay
        
    def run(self):
        ext = self.image_file.split('.')[-1]
        if ext == "pdf":
            image = convert_from_path(self.image_file)
            image = np.asanyarray(image[0])
        else:
            image = cv2.imread(self.image_file)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        h, w, ch = image.shape
        bytes_per_line = ch * w
        qt_frame = QtGui.QImage(image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        qt_image = qt_frame.scaled(self.__frame_size[0], self.__frame_size[1], QtCore.Qt.KeepAspectRatio)
        self.frame_signal.emit(qt_image)
        sleep(self.__default_delay)
        self.done_signal.emit()