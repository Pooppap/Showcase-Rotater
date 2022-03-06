import cv2
import numpy as np

from time import sleep
from PyQt5 import QtGui
from PyQt5 import QtCore
from pdf2image import convert_from_path


class VideoQThread(QtCore.QObject):
    frame_signal = QtCore.pyqtSignal(QtGui.QImage)
    
    def __init__(self, default_delay=30.0):
        super().__init__()
        self.__image_file = None
        self.__frame_size = (1920, 1080)
        self.__default_delay = default_delay
        
    @property
    def image_file(self):
        return self.__image_file
    
    @image_file.setter
    def image_file(self, value):
        assert isinstance(value, str)
        self.__image_file = value
        
    @property
    def frame_size(self):
        return self.__frame_size
    
    @frame_size.setter
    def frame_size(self, value):
        assert isinstance(value, (tuple, list))
        self.__frame_size = value
        
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