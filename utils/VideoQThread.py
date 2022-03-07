import cv2

from time import sleep
from PyQt5 import QtGui
from PyQt5 import QtCore


class VideoQThread(QtCore.QObject):
    frame_signal = QtCore.pyqtSignal(QtGui.QImage)
    done_signal = QtCore.pyqtSignal()
    
    def __init__(self, video_file, frame_size, default_fps=30.0):
        super().__init__()
        self.__video_file = video_file
        self.__frame_size = frame_size
        self.__default_fps = default_fps
        
    def run(self):
        cap = cv2.VideoCapture(self.video_file)
        fps = cap.get(cv2.CAP_PROP_FPS)
        fps = fps if fps else self.__default_fps
        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_frame = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
                qt_image = qt_frame.scaled(self.__frame_size[0], self.__frame_size[1], QtCore.Qt.KeepAspectRatio)
                self.frame_signal.emit(qt_image)
                sleep(1 / fps)
                
            else:
                break
            
        cap.release()
        self.done_signal.emit()