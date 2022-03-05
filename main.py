import sys
import time

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from utils import VideoQThread

if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)

if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)


class App(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.__key_ctrl = False
        self.video_thread = VideoQThread()
        
        self.init_ui()
        self.run()
        
    def init_ui(self):
        self.resize(1920, 1080)
        self.showFullScreen()
        
        self.main_frame = QtWidgets.QLabel(self)
        self.main_frame.resize(1920, 1080)
        
        self.video_thread.video_file = "./test/test.mp4"
        self.video_thread.frame_size = (self.size().width(), self.size().height())
        
        self.show()
        
    def run(self):
        self.thread_pool = QtCore.QThreadPool()
        self.thread_pool.setMaxThreadCount(2)
        self.video_thread.frame_signal.frame_signal.connect(self.update_frame)
        self.thread_pool.start(self.video_thread)
        
    @QtCore.pyqtSlot(QtGui.QImage)
    def update_frame(self, image):
        self.main_frame.setPixmap(QtGui.QPixmap.fromImage(image))
        
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.__key_ctrl = True
            
    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Control:
            self.__key_ctrl = False
            
        if event.key() == QtCore.Qt.Key_Q:
            if self.__key_ctrl:
                self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    app.exec_()
