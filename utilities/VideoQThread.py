import cv2

from PyQt5 import QtGui
from PyQt5 import QtCore


class VideoQThread(QtCore.QRunnable):
    
    def __init__(self):
        super().__init__()
        self.__video_file = None
        self.__frame_size = (1920, 1080)
        self.frame_signal = QtCore.pyqtSignal(QtGui.QImage)
        
    @property
    def video_file(self):
        return self.__video_file
    
    @video_file.setter
    def video_file(self, value):
        assert isinstance(value, str)
        self.__video_file = value
        
    @property
    def frame_size(self):
        return self.__frame_size
    
    @frame_size.setter
    def frame_size(self, value):
        assert isinstance(value, (tuple, list))
        self.__frame_size = value
        
    @QtCore.pyqtSlot()
    def run(self):
        cap = cv2.VideoCapture(self.video_file)
        while True:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_frame = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                qt_image = qt_frame.scaled(self.__frame_size[0], self.__frame_size[1], QtCore.Qt.KeepAspectRatio)
                self.frame_signal.emit(qt_image)